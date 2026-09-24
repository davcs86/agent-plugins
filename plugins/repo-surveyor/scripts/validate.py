#!/usr/bin/env python3
"""Integrity validator for the repo-surveyor plugin.

repo-surveyor is a multi-tool plugin (Claude Code + Cursor + Codex): one shared skills/agents tree
with a manifest for each tool, THREE skills (debt-radar, feature-gap, signal-map) that share one
governance set + config, four read-only advisory subagents, and a committed `claude plugin eval`
regression suite. Python 3 stdlib only (no dependencies, so it runs in CI as-is). Checks:

  1. every tool's plugin manifest (.claude-plugin/plugin.json, .cursor-plugin/plugin.json,
     .codex-plugin/plugin.json) and any repo marketplace.json parse and carry required fields;
  2. every skill SKILL.md and agent .md has YAML frontmatter with the required keys, and no
     frontmatter value has an unquoted ': ' that makes YAML silently drop the whole block;
  3. every agent declares `readonly: true` — these are advisory read-only subagents by contract
     (RS-3), and a subagent that could write would break the "orchestrator is the sole writer"
     invariant;
  4. every reference/... and templates/... path named in a skill's markdown resolves to a file,
     and every skill ships at least one findings template;
  5. no absolute host path leaks into the plugin (portability guard);
  6. the reference files shared across the three skills (principles.md, config-protocol.md,
     severity-rubric.md) are byte-identical — the skills are self-contained, so copies must never
     drift;
  7. no orphan agents: every agents/*.md is referenced by name in some SKILL.md, and every skill
     names at least one subagent (each orchestrator spawns one);
  8. the eval suite is well-formed: each case has a prompt.md with frontmatter, at least one
     grader with a known `type`, every skill-invocation grader references a real skill name, and
     every skill is covered by at least one such grader — so a renamed skill can't silently
     orphan its regression coverage.

Usage:
  python3 validate.py [--plugin-root PATH]   # validate (default root: this script's parent dir)
  python3 validate.py --self-test            # run the built-in negative-fixture tests

Exit 0 when clean; exit 1 with one MISSING:/LEAK:/DRIFT:/YAML:/EVAL:/ERROR: line per finding.
"""

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
INTERNAL_PATH_RE = re.compile(r"(?:reference|templates)/[A-Za-z0-9_./-]+\.md")
# A single-line `key: value` frontmatter entry, capturing the value.
FRONTMATTER_SCALAR_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*:\s+(?P<val>\S.*)$")
# Portability guard: a portable, repo-agnostic plugin must never carry an absolute path from the
# machine it was authored on. Generic illustrative paths (src/foo, apps/web, path/to/...) are
# legitimate examples in this plugin's content, so they are deliberately NOT guarded here.
LEAK_PATTERNS = ("/home/", "/Users/", "/root/")
# README/docs may name the hosting marketplace in install instructions.
LEAK_ALLOWED_LINE_RE = re.compile(r"davcs86/agent-plugins|@davcs86-agent-plugins")
SKILL_REQUIRED_KEYS = ("name", "description")
AGENT_REQUIRED_KEYS = ("name", "description", "tools", "model", "readonly")
SHARED_REFERENCE_FILES = ("principles.md", "config-protocol.md", "severity-rubric.md")
GRADER_TYPES = ("regex", "tool_used", "tool_order", "file_exists", "llm", "baseline")


def frontmatter_block(text):
    match = FRONTMATTER_RE.match(text)
    return match.group(1) if match else None


def frontmatter_keys(text):
    block = frontmatter_block(text)
    if block is None:
        return None
    keys = set()
    for line in block.splitlines():
        key_match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):", line)
        if key_match:
            keys.add(key_match.group(1))
    return keys


def frontmatter_scalars(text):
    """Map of the single-line scalar frontmatter entries (value stripped of surrounding quotes)."""
    block = frontmatter_block(text)
    out = {}
    if block is None:
        return out
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            val = m.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                val = val[1:-1]
            out[m.group(1)] = val
    return out


def check_manifest(path, required, findings):
    if not path.is_file():
        findings.append(f"MISSING: {path} does not exist")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        findings.append(f"ERROR: {path} is not valid JSON ({exc})")
        return None
    for field in required:
        if field not in data:
            findings.append(f"MISSING: {path} lacks required field '{field}'")
    return data


def frontmatter_yaml_risks(block):
    """Lines whose unquoted scalar value contains ': ' (colon-space).

    YAML reads a colon-space inside a plain scalar as a nested mapping and rejects the whole
    block, so at load time *every* frontmatter field is silently dropped (name, description,
    allowed-tools, ...). A real YAML parser catches this, but this validator is stdlib-only;
    quoting the value (e.g. `description: "... Usage: foo ..."`) fixes it.
    """
    risky = []
    for line in block.splitlines():
        m = FRONTMATTER_SCALAR_RE.match(line)
        if m and m.group("val")[:1] not in ("'", '"') and ": " in m.group("val"):
            risky.append(line.strip())
    return risky


def check_frontmatter(path, required, findings):
    text = path.read_text(encoding="utf-8")
    block = frontmatter_block(text)
    if block is None:
        findings.append(f"MISSING: {path} has no YAML frontmatter")
        return
    keys = frontmatter_keys(text)
    for key in required:
        if key not in keys:
            findings.append(f"MISSING: {path} frontmatter lacks '{key}'")
    for line in frontmatter_yaml_risks(block):
        findings.append(f"YAML: {path} frontmatter value has an unquoted ': ' that breaks YAML "
                        f"parsing (all fields silently dropped) — quote it: {line[:70]}")


def check_agent_readonly(path, findings):
    """Advisory subagents must declare readonly: true (RS-3 — the orchestrator is the sole writer)."""
    scalars = frontmatter_scalars(path.read_text(encoding="utf-8"))
    val = scalars.get("readonly")
    if val is not None and val.lower() != "true":
        findings.append(f"ERROR: {path} declares readonly '{val}' — repo-surveyor subagents must be "
                        f"readonly: true (advisory only)")


def check_internal_paths(skill_dir, findings):
    sources = [skill_dir / "SKILL.md"] + sorted((skill_dir / "reference").glob("*.md"))
    for source in sources:
        if not source.is_file():
            continue
        for ref in sorted(set(INTERNAL_PATH_RE.findall(source.read_text(encoding="utf-8")))):
            if not (skill_dir / ref).is_file():
                findings.append(f"MISSING: {source} references '{ref}' which does not exist under {skill_dir}")


def check_skill_has_template(skill_dir, findings):
    templates = list((skill_dir / "templates").glob("*.md")) if (skill_dir / "templates").is_dir() else []
    if not templates:
        findings.append(f"MISSING: skill {skill_dir.name} ships no findings template under templates/")


def check_leakage(plugin_root, findings):
    for path in sorted(plugin_root.rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".json", ".py"):
            continue
        if path.name == "validate.py":
            continue  # the patterns themselves live here
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern in LEAK_PATTERNS:
                if pattern in line and not LEAK_ALLOWED_LINE_RE.search(line):
                    findings.append(f"LEAK: {path}:{lineno} contains host-path string '{pattern}'")


def check_shared_copies(plugin_root, findings):
    for name in SHARED_REFERENCE_FILES:
        copies = sorted((plugin_root / "skills").glob(f"*/reference/{name}"))
        if len(copies) < 2:
            continue
        baseline = copies[0].read_text(encoding="utf-8")
        for copy in copies[1:]:
            if copy.read_text(encoding="utf-8") != baseline:
                findings.append(f"DRIFT: {copy} differs from {copies[0]} — shared reference copies must be identical")


def check_agent_wiring(plugin_root, skill_names, agent_names, findings):
    """Every agent is named by some SKILL.md; every skill names at least one agent."""
    skill_texts = {}
    for name in skill_names:
        skill_md = plugin_root / "skills" / name / "SKILL.md"
        if skill_md.is_file():
            skill_texts[name] = skill_md.read_text(encoding="utf-8")
    for agent in agent_names:
        if not any(agent in text for text in skill_texts.values()):
            findings.append(f"MISSING: agent '{agent}' is not referenced by any SKILL.md (orphan agent)")
    for name, text in skill_texts.items():
        if not any(agent in text for agent in agent_names):
            findings.append(f"MISSING: skill '{name}' names no subagent — each orchestrator spawns one")


def check_evals(plugin_root, skill_names, findings):
    """The committed `claude plugin eval` suite must stay well-formed and cover every skill.

    A model-calling eval can't run in the stdlib CI, but its *files* can be kept honest for free:
    a renamed skill that orphans its coverage, an empty case, or a grader with no type all surface
    here rather than at the next expensive eval run.
    """
    evals_dir = plugin_root / "evals"
    if not evals_dir.is_dir():
        findings.append(f"MISSING: {evals_dir} does not exist — the eval suite is part of this plugin")
        return
    case_dirs = [d for d in sorted(evals_dir.glob("*")) if d.is_dir() and d.name != "results"]
    if not case_dirs:
        findings.append(f"MISSING: no eval cases under {evals_dir}")
        return

    covered_skills = set()
    for case in case_dirs:
        if not (case / "prompt.md").is_file():
            findings.append(f"EVAL: case '{case.name}' has no prompt.md")
        else:
            if frontmatter_keys((case / "prompt.md").read_text(encoding="utf-8")) is None:
                findings.append(f"EVAL: {case / 'prompt.md'} has no YAML frontmatter")
        graders = sorted((case / "graders").glob("*.md")) if (case / "graders").is_dir() else []
        if not graders:
            findings.append(f"EVAL: case '{case.name}' has no graders/*.md")
        for grader in graders:
            scalars = frontmatter_scalars(grader.read_text(encoding="utf-8"))
            gtype = scalars.get("type")
            if gtype is None:
                findings.append(f"EVAL: {grader} has no 'type'")
            elif gtype not in GRADER_TYPES:
                findings.append(f"EVAL: {grader} has unknown grader type '{gtype}'")
            if scalars.get("tool") == "Skill" and "input_match" in scalars:
                match = scalars["input_match"]
                hit = next((s for s in skill_names if s in match), None)
                if hit is None:
                    findings.append(f"EVAL: {grader} input_match references no known skill "
                                    f"(skills: {', '.join(sorted(skill_names))})")
                else:
                    covered_skills.add(hit)
    for name in sorted(skill_names):
        if name not in covered_skills:
            findings.append(f"EVAL: skill '{name}' has no eval case asserting it fired "
                            f"(add a tool_used Skill grader referencing it)")


def validate(plugin_root):
    findings = []
    check_manifest(plugin_root / ".claude-plugin" / "plugin.json", ("name", "description", "version"), findings)
    check_manifest(plugin_root / ".cursor-plugin" / "plugin.json", ("name", "description", "version"), findings)
    check_manifest(plugin_root / ".codex-plugin" / "plugin.json", ("name", "description", "version"), findings)

    skills_dir = plugin_root / "skills"
    skill_dirs = sorted(d for d in skills_dir.glob("*") if d.is_dir()) if skills_dir.is_dir() else []
    if not skill_dirs:
        findings.append(f"MISSING: no skills found under {skills_dir}")
    skill_names = []
    for skill_dir in skill_dirs:
        skill_names.append(skill_dir.name)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            findings.append(f"MISSING: {skill_md} does not exist")
            continue
        check_frontmatter(skill_md, SKILL_REQUIRED_KEYS, findings)
        check_internal_paths(skill_dir, findings)
        check_skill_has_template(skill_dir, findings)

    agent_files = sorted((plugin_root / "agents").glob("*.md"))
    if not agent_files:
        findings.append(f"MISSING: no agents found under {plugin_root / 'agents'}")
    agent_names = []
    for agent_file in agent_files:
        check_frontmatter(agent_file, AGENT_REQUIRED_KEYS, findings)
        check_agent_readonly(agent_file, findings)
        scalars = frontmatter_scalars(agent_file.read_text(encoding="utf-8"))
        agent_names.append(scalars.get("name", agent_file.stem))

    check_leakage(plugin_root, findings)
    check_shared_copies(plugin_root, findings)
    if skill_names and agent_names:
        check_agent_wiring(plugin_root, skill_names, agent_names, findings)
    if skill_names:
        check_evals(plugin_root, set(skill_names), findings)

    # Marketplace entries (only when the plugin sits inside a marketplace repo) — one catalog per
    # tool, all pointing at this same plugin tree. Each tool's catalog has its own required
    # top-level fields (Codex uses `interface`, not the Claude/Cursor `owner`) and its own path.
    repo_root = plugin_root.parent.parent
    marketplace_specs = [
        (repo_root / ".claude-plugin" / "marketplace.json", ("name", "owner", "plugins")),
        (repo_root / ".cursor-plugin" / "marketplace.json", ("name", "owner", "plugins")),
        (repo_root / ".agents" / "plugins" / "marketplace.json", ("name", "interface", "plugins")),
    ]
    for marketplace, required in marketplace_specs:
        if not marketplace.is_file():
            continue
        data = check_manifest(marketplace, required, findings)
        if data and isinstance(data.get("plugins"), list):
            for entry in data["plugins"]:
                source = entry.get("source", "")
                if isinstance(source, str) and source.startswith("./"):
                    if not (repo_root / source).is_dir():
                        findings.append(f"MISSING: {marketplace} plugin source '{source}' does not resolve")
    return findings


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def self_test():
    failures = []

    def expect(label, findings, needle):
        if not any(needle in f for f in findings):
            failures.append(f"self-test '{label}': expected a finding containing '{needle}', got {findings}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "broken-plugin"
        (root / ".claude-plugin").mkdir(parents=True)
        # Valid JSON missing required fields:
        _write(root / ".claude-plugin" / "plugin.json", '{"version": "0.0.1"}')
        # Skill 'alpha': missing 'description'; dangling internal ref; no template; names no agent:
        _write(root / "skills" / "alpha" / "SKILL.md",
               "---\nname: alpha\n---\nLoad `reference/missing.md` and read /home/alice/secret.txt.\n")
        _write(root / "skills" / "alpha" / "reference" / "principles.md", "version A\n")
        # Skill 'beta': unquoted colon-space in description (YAML-breaking); has a template; names an agent:
        _write(root / "skills" / "beta" / "SKILL.md",
               "---\nname: beta\ndescription: Turn X into Y. Usage: run it\n---\nSpawn the scout subagent.\n")
        _write(root / "skills" / "beta" / "reference" / "principles.md", "version B\n")
        _write(root / "skills" / "beta" / "templates" / "beta-findings.md", "# t\n")
        # Agent: has frontmatter but readonly is false (contract violation); named 'scout':
        _write(root / "agents" / "scout.md",
               "---\nname: scout\ndescription: d\ntools: Read\nmodel: inherit\nreadonly: false\n---\nbody\n")
        # Orphan agent: never named by any SKILL.md.
        _write(root / "agents" / "orphan.md",
               "---\nname: orphan\ndescription: d\ntools: Read\nmodel: inherit\nreadonly: true\n---\nbody\n")
        # Eval case: prompt present, but grader has an unknown type and references no known skill.
        _write(root / "evals" / "case1" / "prompt.md", "---\nname: case1\n---\nprompt body\n")
        _write(root / "evals" / "case1" / "graders" / "g.md",
               "---\ntype: bogus\ntool: Skill\ninput_match: '\"skill\": \"nonesuch\"'\n---\n")

        findings = validate(root)
        expect("missing manifest field", findings, "lacks required field 'name'")
        expect("missing frontmatter key", findings, "frontmatter lacks 'description'")
        expect("dangling internal ref", findings, "references 'reference/missing.md'")
        expect("leakage", findings, "host-path string '/home/'")
        expect("colon-space yaml", findings, "YAML:")
        expect("shared copy drift", findings, "DRIFT:")
        expect("no template", findings, "ships no findings template")
        expect("agent not readonly", findings, "must be readonly: true")
        expect("orphan agent", findings, "orphan agent")
        expect("skill names no agent", findings, "names no subagent")
        expect("unknown grader type", findings, "unknown grader type 'bogus'")
        expect("input_match no known skill", findings, "references no known skill")
        expect("skill not covered by eval", findings, "has no eval case asserting it fired")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "bad-json-plugin"
        (root / ".claude-plugin").mkdir(parents=True)
        _write(root / ".claude-plugin" / "plugin.json", "{not json")
        expect("invalid JSON", validate(root), "is not valid JSON")

    if failures:
        print("\n".join(failures))
        return 1
    print("self-test: all negative fixtures caught OK")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plugin-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    findings = validate(args.plugin_root)
    if findings:
        print("\n".join(findings))
        return 1
    print(f"OK: {args.plugin_root} passed all checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())

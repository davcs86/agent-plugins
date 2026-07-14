#!/usr/bin/env python3
"""Integrity validator for the design-buddy plugin.

design-buddy is a dual-tool plugin (Claude Code + Cursor): one shared skills/agents tree with a
manifest for each tool. Python 3 stdlib only (plugin script policy: Python, never Bash). Checks:
  1. both plugin manifests (.claude-plugin/plugin.json, .cursor-plugin/plugin.json) and any repo
     marketplace.json parse and carry required fields;
  2. every skill SKILL.md and agent .md has YAML frontmatter with the required keys (agents carry
     `readonly` so Cursor enforces the read-only contract that Claude expresses via `tools`), and
     no frontmatter value has an unquoted ': ' that makes YAML silently drop the whole block;
  3. every reference/... and templates/... path named in a skill's markdown resolves to a file;
  4. no host-repo-specific strings leak into the plugin (portability guard);
  5. shared reference files duplicated across skills (principles.md, config-protocol.md) are
     byte-identical — the skills are self-contained, so copies must never drift.

Usage:
  python3 validate.py [--plugin-root PATH]   # validate (default root: this script's parent dir)
  python3 validate.py --self-test            # run the built-in negative-fixture tests

Exit 0 when clean; exit 1 with one MISSING:/LEAK:/ERROR: line per finding.
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
# "xstockstrat" stays here as an origin-leak guard: this plugin was exported
# from that repo and none of its host-specific strings should reappear.
LEAK_PATTERNS = ("xstockstrat", "docs/roadmap", "docs/sdd", "services/")
# README may name the hosting marketplace in install instructions.
LEAK_ALLOWED_LINE_RE = re.compile(r"davcs86/agent-plugins|@davcs86-agent-plugins")
SKILL_REQUIRED_KEYS = ("name", "description")
AGENT_REQUIRED_KEYS = ("name", "description", "tools", "model", "readonly")
SHARED_REFERENCE_FILES = ("principles.md", "config-protocol.md")


def frontmatter_keys(text):
    match = FRONTMATTER_RE.match(text)
    if match is None:
        return None
    keys = set()
    for line in match.group(1).splitlines():
        key_match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):", line)
        if key_match:
            keys.add(key_match.group(1))
    return keys


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
    match = FRONTMATTER_RE.match(text)
    if match is None:
        findings.append(f"MISSING: {path} has no YAML frontmatter")
        return
    keys = frontmatter_keys(text)
    for key in required:
        if key not in keys:
            findings.append(f"MISSING: {path} frontmatter lacks '{key}'")
    for line in frontmatter_yaml_risks(match.group(1)):
        findings.append(f"YAML: {path} frontmatter value has an unquoted ': ' that breaks YAML "
                        f"parsing (all fields silently dropped) — quote it: {line[:70]}")


def check_internal_paths(skill_dir, findings):
    sources = [skill_dir / "SKILL.md"] + sorted((skill_dir / "reference").glob("*.md"))
    for source in sources:
        if not source.is_file():
            continue
        for ref in sorted(set(INTERNAL_PATH_RE.findall(source.read_text(encoding="utf-8")))):
            if not (skill_dir / ref).is_file():
                findings.append(f"MISSING: {source} references '{ref}' which does not exist under {skill_dir}")


def check_leakage(plugin_root, findings):
    for path in sorted(plugin_root.rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".json", ".py"):
            continue
        if path.name == "validate.py":
            continue  # the patterns themselves live here
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern in LEAK_PATTERNS:
                if pattern in line and not LEAK_ALLOWED_LINE_RE.search(line):
                    findings.append(f"LEAK: {path}:{lineno} contains host-repo string '{pattern}'")


def check_shared_copies(plugin_root, findings):
    for name in SHARED_REFERENCE_FILES:
        copies = sorted((plugin_root / "skills").glob(f"*/reference/{name}"))
        if len(copies) < 2:
            continue
        baseline = copies[0].read_text(encoding="utf-8")
        for copy in copies[1:]:
            if copy.read_text(encoding="utf-8") != baseline:
                findings.append(f"DRIFT: {copy} differs from {copies[0]} — shared reference copies must be identical")


def validate(plugin_root):
    findings = []
    check_manifest(plugin_root / ".claude-plugin" / "plugin.json", ("name", "description", "version"), findings)
    check_manifest(plugin_root / ".cursor-plugin" / "plugin.json", ("name", "description", "version"), findings)

    skills_dir = plugin_root / "skills"
    skill_dirs = sorted(d for d in skills_dir.glob("*") if d.is_dir()) if skills_dir.is_dir() else []
    if not skill_dirs:
        findings.append(f"MISSING: no skills found under {skills_dir}")
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            findings.append(f"MISSING: {skill_md} does not exist")
            continue
        check_frontmatter(skill_md, SKILL_REQUIRED_KEYS, findings)
        check_internal_paths(skill_dir, findings)

    agent_files = sorted((plugin_root / "agents").glob("*.md"))
    if not agent_files:
        findings.append(f"MISSING: no agents found under {plugin_root / 'agents'}")
    for agent_file in agent_files:
        check_frontmatter(agent_file, AGENT_REQUIRED_KEYS, findings)

    check_leakage(plugin_root, findings)
    check_shared_copies(plugin_root, findings)

    # Marketplace entries (only when the plugin sits inside a marketplace repo) — one catalog per
    # tool, both pointing at this same plugin tree.
    repo_root = plugin_root.parent.parent
    for catalog_dir in (".claude-plugin", ".cursor-plugin"):
        marketplace = repo_root / catalog_dir / "marketplace.json"
        if not marketplace.is_file():
            continue
        data = check_manifest(marketplace, ("name", "owner", "plugins"), findings)
        if data and isinstance(data.get("plugins"), list):
            for entry in data["plugins"]:
                source = entry.get("source", "")
                if isinstance(source, str) and source.startswith("./"):
                    if not (repo_root / source).is_dir():
                        findings.append(f"MISSING: {marketplace} plugin source '{source}' does not resolve")
    return findings


def self_test():
    failures = []

    def expect(label, findings, needle):
        if not any(needle in f for f in findings):
            failures.append(f"self-test '{label}': expected a finding containing '{needle}', got {findings}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "broken-plugin"
        (root / ".claude-plugin").mkdir(parents=True)
        # Valid JSON missing required fields:
        (root / ".claude-plugin" / "plugin.json").write_text('{"version": "0.0.1"}', encoding="utf-8")
        skill = root / "skills" / "demo"
        (skill / "reference").mkdir(parents=True)
        # Frontmatter missing 'description'; dangling internal reference; host-repo leakage:
        (skill / "SKILL.md").write_text(
            "---\nname: demo\n---\nLoad `reference/missing.md` and copy from services/foo.\n",
            encoding="utf-8",
        )
        (root / "agents").mkdir()
        (root / "agents" / "bare.md").write_text("No frontmatter here.\n", encoding="utf-8")
        # Drifted shared reference copies across two skills:
        (skill / "reference" / "principles.md").write_text("version A\n", encoding="utf-8")
        skill2 = root / "skills" / "demo2"
        (skill2 / "reference").mkdir(parents=True)
        # Unquoted colon-space in the description would make YAML drop the whole block:
        (skill2 / "SKILL.md").write_text("---\nname: demo2\ndescription: Turn X into Y. Usage: run it\n---\nBody.\n", encoding="utf-8")
        (skill2 / "reference" / "principles.md").write_text("version B\n", encoding="utf-8")
        findings = validate(root)
        expect("missing manifest field", findings, "lacks required field 'name'")
        expect("missing frontmatter key", findings, "frontmatter lacks 'description'")
        expect("dangling internal ref", findings, "references 'reference/missing.md'")
        expect("agent frontmatter", findings, "bare.md has no YAML frontmatter")
        expect("leakage", findings, "host-repo string 'services/'")
        expect("shared copy drift", findings, "DRIFT:")
        expect("colon-space yaml", findings, "YAML:")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "bad-json-plugin"
        (root / ".claude-plugin").mkdir(parents=True)
        (root / ".claude-plugin" / "plugin.json").write_text("{not json", encoding="utf-8")
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

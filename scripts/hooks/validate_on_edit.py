#!/usr/bin/env python3
"""PostToolUse hook: re-validate marketplace manifests right after they're edited.

Reads the Claude Code hook JSON payload from stdin. If the edited file is a marketplace
catalog or a plugin manifest, reruns `scripts/validate_manifests.py` (and, if the edit
was inside a plugin directory, that plugin's own `scripts/validate.py` when it has one)
so a semver or parity mistake surfaces immediately instead of waiting for CI.

**Everything here is anchored to the repo root, never to the working directory.**
``REPO_ROOT`` is derived from ``__file__``, the subprocesses run with ``cwd=REPO_ROOT``,
and a relative ``file_path`` in the payload is resolved against the repo root rather
than against wherever the session happens to be sitting. The hook must behave
identically whether the session was started at the repo root, in a subdirectory, or in
a git worktree — a session that ``cd``s somewhere else must not silently stop
validating. The matching half of that contract lives in ``.claude/settings.json``,
whose command is ``$CLAUDE_PROJECT_DIR``-anchored for the same reason.

Run with ``--self-test`` to execute the built-in suite (same convention as
``scripts/validate_manifests.py`` and the per-plugin validators).

Python 3 stdlib only, matching the rest of this repo's tooling policy.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RELEVANT_RE = re.compile(
    r"(^|/)\.(claude|cursor)-plugin/(marketplace|plugin)\.json$"
    r"|(^|/)\.codex-plugin/plugin\.json$"
    r"|(^|/)\.agents/plugins/marketplace\.json$"
)


def repo_relative(file_path, root=REPO_ROOT):
    """Return ``file_path`` as a path relative to ``root``, or None if it is outside it.

    An absolute path is resolved as given. A **relative** path is resolved against
    ``root`` — not the process's working directory — so the hook identifies the same
    file no matter where the session was started. Resolving it against the cwd would
    make a hook run from a subdirectory quietly decide the edit was out of scope and
    skip validation, which is worse than failing loudly.
    """
    candidate = Path(file_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve().relative_to(Path(root).resolve())
    except ValueError:
        return None


def commands_for(rel, root=REPO_ROOT):
    """Return the validator commands to run for a repo-relative edited path.

    Empty list => the edit is out of scope and the hook does nothing. Commands are
    repo-relative and are always run with ``cwd=root``.
    """
    if rel is None or not RELEVANT_RE.search(rel.as_posix()):
        return []

    commands = [[sys.executable, "scripts/validate_manifests.py"]]
    if rel.parts[0] == "plugins" and len(rel.parts) > 1:
        plugin_validator = Path(root) / "plugins" / rel.parts[1] / "scripts" / "validate.py"
        if plugin_validator.is_file():
            commands.append([sys.executable, str(Path("plugins") / rel.parts[1] / "scripts" / "validate.py")])
    return commands


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path:
        return 0

    rel = repo_relative(file_path)
    commands = commands_for(rel)
    if not commands:
        return 0

    failed = False
    for cmd in commands:
        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            failed = True
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)

    if failed:
        sys.stderr.write(f"\nManifest validation failed after editing {rel} — fix before "
                          f"committing.\n")
        return 2

    return 0


# ---------------------------------------------------------------------------
# Self-test suite (--self-test). The point of most of these is cwd-independence:
# the hook is invoked by the agent harness, which makes no promise about the
# working directory, so every path decision must come out the same regardless.
# ---------------------------------------------------------------------------

def self_test():
    failures = []

    def check(label, got, want):
        if got != want:
            failures.append(f"{label}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        (root / ".claude-plugin").mkdir(parents=True)
        (root / ".claude-plugin" / "marketplace.json").write_text("{}", encoding="utf-8")
        for name in ("alpha", "beta"):
            (root / "plugins" / name / ".claude-plugin").mkdir(parents=True)
            (root / "plugins" / name / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
        # alpha ships its own validator; beta deliberately does not.
        (root / "plugins" / "alpha" / "scripts").mkdir(parents=True)
        (root / "plugins" / "alpha" / "scripts" / "validate.py").write_text("", encoding="utf-8")

        cat = ".claude-plugin/marketplace.json"
        alpha = "plugins/alpha/.claude-plugin/plugin.json"
        beta = "plugins/beta/.claude-plugin/plugin.json"

        # 1. An absolute path inside the repo resolves to its repo-relative form.
        check("absolute path", repo_relative(str(root / cat), root), Path(cat))

        # 2. A RELATIVE path resolves against the repo root, not the cwd. This is the
        #    regression that made a `cd`-ed session stop validating silently.
        check("relative path", repo_relative(cat, root), Path(cat))

        # 3. A path outside the repo is out of scope, not an error.
        check("outside repo", repo_relative("/etc/passwd", root), None)

        # 4. Catalog edit => marketplace validator only.
        check("catalog commands",
              [c[1:] for c in commands_for(Path(cat), root)],
              [["scripts/validate_manifests.py"]])

        # 5. Plugin manifest edit, plugin ships a validator => both run.
        check("plugin with validator",
              [c[1:] for c in commands_for(Path(alpha), root)],
              [["scripts/validate_manifests.py"],
               [str(Path("plugins/alpha/scripts/validate.py"))]])

        # 6. Plugin manifest edit, no validator => marketplace validator only.
        check("plugin without validator",
              [c[1:] for c in commands_for(Path(beta), root)],
              [["scripts/validate_manifests.py"]])

        # 6b. Codex plugin manifest and repo marketplace catalog are relevant too —
        #     a different manifest filename/path shape than Claude's and Cursor's.
        codex_plugin = "plugins/alpha/.codex-plugin/plugin.json"
        codex_cat = ".agents/plugins/marketplace.json"
        check("codex plugin manifest",
              [c[1:] for c in commands_for(Path(codex_plugin), root)],
              [["scripts/validate_manifests.py"],
               [str(Path("plugins/alpha/scripts/validate.py"))]])
        check("codex marketplace catalog",
              [c[1:] for c in commands_for(Path(codex_cat), root)],
              [["scripts/validate_manifests.py"]])

        # 7. Non-manifest edits are out of scope (AP-13: editing a SKILL.md or the
        #    validator itself triggers nothing — run the validators by hand).
        for path in ("plugins/alpha/skills/foo/SKILL.md", "README.md",
                     "scripts/validate_manifests.py", ".claude-plugin/other.json"):
            check(f"out of scope: {path}", commands_for(Path(path), root), [])

        # 8. An unresolvable path yields no commands rather than raising.
        check("None path", commands_for(None, root), [])

    # 9. The settings that invoke this hook must themselves be root-anchored.
    #    Everything above tests the script; this tests the one line that actually
    #    broke — a bare `python3 scripts/hooks/...` command resolves against the
    #    session's cwd and dies the moment a session works from a subdirectory.
    #    Without this case, reverting settings.json would leave CI green.
    settings_path = REPO_ROOT / ".claude" / "settings.json"
    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"settings.json is not valid JSON: {exc}")
            settings = {}
        for group in settings.get("hooks", {}).get("PostToolUse", []):
            for hook in group.get("hooks", []):
                command = hook.get("command", "")
                if "validate_on_edit.py" not in command:
                    continue
                if "CLAUDE_PROJECT_DIR" not in command and not command.strip().startswith("/"):
                    failures.append(
                        "settings.json invokes the hook with a working-directory-relative "
                        f"path ({command!r}) — anchor it to \"${{CLAUDE_PROJECT_DIR:-.}}\" or an "
                        "absolute path, or it breaks for any session not started at the repo root")

    if failures:
        print(f"SELF-TEST FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("SELF-TEST PASSED: hook path resolution is working-directory independent.")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        sys.exit(self_test())
    sys.exit(main())

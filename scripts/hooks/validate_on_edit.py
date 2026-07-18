#!/usr/bin/env python3
"""PostToolUse hook: re-validate marketplace manifests right after they're edited.

Reads the Claude Code hook JSON payload from stdin. If the edited file is a marketplace
catalog or a plugin manifest, reruns `scripts/validate_manifests.py` (and, if the edit
was inside a plugin directory, that plugin's own `scripts/validate.py` when it has one)
so a semver or parity mistake surfaces immediately instead of waiting for CI.

Python 3 stdlib only, matching the rest of this repo's tooling policy.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RELEVANT_RE = re.compile(r"(^|/)\.(claude|cursor)-plugin/(marketplace|plugin)\.json$")


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path:
        return 0

    try:
        rel = Path(file_path).resolve().relative_to(REPO_ROOT)
    except ValueError:
        return 0

    if not RELEVANT_RE.search(rel.as_posix()):
        return 0

    commands = [[sys.executable, "scripts/validate_manifests.py"]]
    if rel.parts[0] == "plugins":
        plugin_validator = REPO_ROOT / "plugins" / rel.parts[1] / "scripts" / "validate.py"
        if plugin_validator.is_file():
            commands.append([sys.executable, str(plugin_validator.relative_to(REPO_ROOT))])

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


if __name__ == "__main__":
    sys.exit(main())

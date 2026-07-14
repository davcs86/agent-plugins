#!/usr/bin/env python3
"""Validate the multi-agent plugin marketplace manifests.

This script is dependency-free (standard library only) so it runs anywhere
without a `pip install` step, including in CI.

It checks, for each supported agent tool (Claude Code and Cursor):

1. The tool's top-level ``marketplace.json`` exists and is valid JSON.
2. The marketplace has the required top-level fields (``name``, ``plugins``).
3. Every plugin listed in ``marketplace.json`` resolves to a directory under
   ``plugins/<name>/`` that contains the tool-specific plugin manifest.

It prints a clear pass/fail summary and exits non-zero on any failure so it
can gate a CI pipeline.

Adding a new agent tool later is a matter of appending an entry to ``TOOLS``.
"""

import json
import sys
from pathlib import Path

# Repository root (this file lives in <root>/scripts/).
ROOT = Path(__file__).resolve().parent.parent

# Where individual plugins live, one directory each.
PLUGINS_DIR = ROOT / "plugins"

# Per-tool configuration. To support a future agent tool (e.g. Codex), add an
# entry here describing where its marketplace catalog lives and the manifest
# each of its plugins must ship.
TOOLS = [
    {
        "label": "Claude Code",
        "marketplace": ROOT / ".claude-plugin" / "marketplace.json",
        # Manifest that each registered plugin directory must contain.
        "plugin_manifest": Path(".claude-plugin") / "plugin.json",
    },
    {
        "label": "Cursor",
        "marketplace": ROOT / ".cursor-plugin" / "marketplace.json",
        "plugin_manifest": Path(".cursor-plugin") / "plugin.json",
    },
]


def _plugin_dir_name(source, name):
    """Resolve the plugins/ subdirectory name for a marketplace entry.

    ``source`` may be a relative path string (e.g. ``"./plugins/foo"`` or
    ``"foo"`` when a ``pluginRoot`` is configured) or an object describing a
    remote source (github/git). Only local relative-path sources are validated
    against the on-disk ``plugins/`` tree; remote sources are skipped because
    their contents live in another repository.
    """
    if isinstance(source, str):
        # Strip a leading "./" and an optional "plugins/" prefix so both
        # "./plugins/foo" and a pluginRoot-relative "foo" map to "foo".
        rel = source.lstrip("./")
        if rel.startswith("plugins/"):
            rel = rel[len("plugins/"):]
        return rel.strip("/") or name
    # Non-string source => remote (github/git); nothing local to check.
    return None


def validate_tool(tool):
    """Validate one tool's marketplace file. Returns a list of error strings."""
    errors = []
    label = tool["label"]
    marketplace_path = tool["marketplace"]

    if not marketplace_path.exists():
        errors.append(f"[{label}] missing marketplace file: "
                      f"{marketplace_path.relative_to(ROOT)}")
        return errors

    try:
        data = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"[{label}] invalid JSON in "
                      f"{marketplace_path.relative_to(ROOT)}: {exc}")
        return errors

    if not isinstance(data, dict):
        errors.append(f"[{label}] marketplace root must be a JSON object")
        return errors

    # Required top-level fields.
    if not data.get("name"):
        errors.append(f"[{label}] marketplace is missing required 'name'")

    plugins = data.get("plugins")
    if plugins is None:
        errors.append(f"[{label}] marketplace is missing required 'plugins' array")
        return errors
    if not isinstance(plugins, list):
        errors.append(f"[{label}] 'plugins' must be an array")
        return errors

    # Validate each plugin entry resolves to a real directory + manifest.
    for index, entry in enumerate(plugins):
        if not isinstance(entry, dict):
            errors.append(f"[{label}] plugins[{index}] must be an object")
            continue

        name = entry.get("name")
        if not name:
            errors.append(f"[{label}] plugins[{index}] is missing required 'name'")
            continue

        source = entry.get("source")
        if source is None:
            errors.append(f"[{label}] plugin '{name}' is missing required 'source'")
            continue

        dir_name = _plugin_dir_name(source, name)
        if dir_name is None:
            # Remote source (github/git) — not validated against local tree.
            continue

        plugin_dir = PLUGINS_DIR / dir_name
        if not plugin_dir.is_dir():
            errors.append(f"[{label}] plugin '{name}' references missing "
                          f"directory: plugins/{dir_name}/")
            continue

        manifest = plugin_dir / tool["plugin_manifest"]
        if not manifest.is_file():
            errors.append(f"[{label}] plugin '{name}' is missing manifest: "
                          f"{manifest.relative_to(ROOT)}")
            continue

        try:
            json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"[{label}] plugin '{name}' has invalid manifest JSON "
                          f"({manifest.relative_to(ROOT)}): {exc}")

    return errors


def main():
    print("Validating agent-tooling marketplace manifests...\n")

    all_errors = []
    for tool in TOOLS:
        errors = validate_tool(tool)
        count = len(tool_plugins(tool))
        status = "FAIL" if errors else "ok"
        print(f"  [{status}] {tool['label']}: {count} plugin(s) registered")
        all_errors.extend(errors)

    print()
    if all_errors:
        print(f"FAILED with {len(all_errors)} error(s):")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("PASSED: all marketplace manifests are valid.")
    return 0


def tool_plugins(tool):
    """Best-effort count of registered plugins for the summary line."""
    path = tool["marketplace"]
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    plugins = data.get("plugins")
    return plugins if isinstance(plugins, list) else []


if __name__ == "__main__":
    sys.exit(main())

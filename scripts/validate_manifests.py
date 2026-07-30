#!/usr/bin/env python3
"""Validate the multi-agent plugin marketplace manifests.

This script is dependency-free (standard library only) so it runs anywhere
without a `pip install` step, including in CI.

It checks, for each supported agent tool (Claude Code, Cursor, and Codex):

1. The tool's top-level ``marketplace.json`` exists and is valid JSON.
2. The marketplace has the required top-level fields (``name``, ``plugins``).
3. Every plugin listed in ``marketplace.json`` resolves to a directory under
   ``plugins/<name>/`` that contains the tool-specific plugin manifest.
4. That manifest's ``version`` is present and is valid MAJOR.MINOR.PATCH
   semver (optionally with a ``-prerelease`` and/or ``+build`` suffix).
5. When a plugin ships manifests for more than one tool, their ``version``
   fields are identical — a mismatch means one tool's users are stuck on a
   stale (or ahead-of-schedule) release.

And across the repo as a whole:

6. **Membership parity** — every local plugin registered in one tool's
   catalog is registered in every other tool's catalog. The repo's core
   invariant is that all catalogs describe the same plugin set; a plugin
   added to one catalog and forgotten in another means that tool's users
   never see it at all.
7. **README listing** — every registered local plugin is mentioned in the
   top-level ``README.md``, the first thing a human reads. A plugin can pass
   every manifest check and still land invisible; this catches that.

It prints a clear pass/fail summary and exits non-zero on any failure so it
can gate a CI pipeline. Run with ``--self-test`` to execute its built-in
test suite against temporary fixture repos (same convention as the
per-plugin ``scripts/validate.py`` validators).

Adding a new agent tool later is a matter of appending an entry to ``TOOLS``.
"""

import json
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# Repository root (this file lives in <root>/scripts/).
ROOT = Path(__file__).resolve().parent.parent

# Per-tool configuration, with paths relative to the repo root so the same
# definitions validate fixture repos in --self-test. To support a future
# agent tool (e.g. Codex), add an entry here describing where its marketplace
# catalog lives and the manifest each of its plugins must ship.
TOOLS = [
    {
        "label": "Claude Code",
        "marketplace": Path(".claude-plugin") / "marketplace.json",
        # Manifest that each registered plugin directory must contain.
        "plugin_manifest": Path(".claude-plugin") / "plugin.json",
    },
    {
        "label": "Cursor",
        "marketplace": Path(".cursor-plugin") / "marketplace.json",
        "plugin_manifest": Path(".cursor-plugin") / "plugin.json",
    },
    {
        "label": "Codex",
        "marketplace": Path(".agents") / "plugins" / "marketplace.json",
        "plugin_manifest": Path(".codex-plugin") / "plugin.json",
    },
]

# MAJOR.MINOR.PATCH, with optional -prerelease and +build metadata suffixes
# (https://semver.org). Deliberately looser than the spec's numeric-only
# prerelease-identifier rule to keep this stdlib-only script simple.
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


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
        # (removeprefix, not lstrip: lstrip strips a character *set*, which
        # would also eat leading dots from a hidden directory name.)
        rel = source.removeprefix("./")
        if rel.startswith("plugins/"):
            rel = rel[len("plugins/"):]
        return rel.strip("/") or name
    # Non-string source => remote (github/git); nothing local to check.
    return None


def validate_tool(root, tool, plugin_versions, tool_members):
    """Validate one tool's marketplace file. Returns a list of error strings.

    ``plugin_versions`` is a ``{plugin_name: {tool_label: version}}`` map and
    ``tool_members`` a ``{tool_label: set(local_plugin_names)}`` map; this
    call adds its findings to both so the caller can cross-check version and
    membership parity across tools once every tool has been validated.
    """
    errors = []
    label = tool["label"]
    marketplace_path = root / tool["marketplace"]
    tool_members.setdefault(label, set())

    if not marketplace_path.exists():
        errors.append(f"[{label}] missing marketplace file: "
                      f"{tool['marketplace']}")
        return errors

    try:
        data = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"[{label}] invalid JSON in {tool['marketplace']}: {exc}")
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

        tool_members[label].add(name)

        plugin_dir = root / "plugins" / dir_name
        if not plugin_dir.is_dir():
            errors.append(f"[{label}] plugin '{name}' references missing "
                          f"directory: plugins/{dir_name}/")
            continue

        manifest = plugin_dir / tool["plugin_manifest"]
        if not manifest.is_file():
            errors.append(f"[{label}] plugin '{name}' is missing manifest: "
                          f"plugins/{dir_name}/{tool['plugin_manifest']}")
            continue

        try:
            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"[{label}] plugin '{name}' has invalid manifest JSON "
                          f"(plugins/{dir_name}/{tool['plugin_manifest']}): {exc}")
            continue

        version = manifest_data.get("version")
        if version is None:
            errors.append(f"[{label}] plugin '{name}' manifest is missing required "
                          f"'version' (plugins/{dir_name}/{tool['plugin_manifest']})")
        elif not isinstance(version, str) or not SEMVER_RE.match(version):
            errors.append(f"[{label}] plugin '{name}' has a non-semver version "
                          f"'{version}' (plugins/{dir_name}/{tool['plugin_manifest']}) "
                          f"— expected MAJOR.MINOR.PATCH, e.g. 1.2.3")
        else:
            plugin_versions[name][label] = version

    return errors


def check_version_parity(plugin_versions):
    """Flag plugins whose semver-valid version differs across tool manifests."""
    errors = []
    for name, versions_by_tool in sorted(plugin_versions.items()):
        distinct = set(versions_by_tool.values())
        if len(distinct) > 1:
            detail = ", ".join(f"{label}={version}"
                                for label, version in sorted(versions_by_tool.items()))
            errors.append(f"plugin '{name}' has mismatched versions across tools: {detail}")
    return errors


def check_membership_parity(tool_members):
    """Flag local plugins registered in one catalog but absent from another.

    The catalogs must describe the same plugin set; a plugin present in only
    some of them silently never reaches the other tools' users — exactly the
    failure this repo exists to prevent.
    """
    errors = []
    all_names = set().union(*tool_members.values()) if tool_members else set()
    for label, members in sorted(tool_members.items()):
        for name in sorted(all_names - members):
            errors.append(f"[{label}] plugin '{name}' is registered in another "
                          f"tool's catalog but missing from this one — register "
                          f"it in every catalog (or remove it everywhere)")
    return errors


def check_readme_mentions(root, tool_members):
    """Flag registered local plugins that the top-level README never mentions.

    The README is the marketplace's human-facing catalog; a plugin that
    passes every manifest check but is absent there ships undocumented.
    """
    readme_path = root / "README.md"
    if not readme_path.is_file():
        # Fixture repos without a README skip this check; the real repo has one.
        return []
    readme = readme_path.read_text(encoding="utf-8")
    all_names = set().union(*tool_members.values()) if tool_members else set()
    return [f"plugin '{name}' is not mentioned in README.md — add it to the "
            f"plugin table so the marketplace's front page stays complete"
            for name in sorted(all_names) if name not in readme]


def validate_repo(root):
    """Run every check against ``root``. Returns (errors, summary_lines)."""
    all_errors = []
    summary = []
    plugin_versions = defaultdict(dict)
    tool_members = {}
    for tool in TOOLS:
        errors = validate_tool(root, tool, plugin_versions, tool_members)
        status = "FAIL" if errors else "ok"
        count = len(tool_members.get(tool["label"], ()))
        summary.append(f"  [{status}] {tool['label']}: {count} plugin(s) registered")
        all_errors.extend(errors)

    all_errors.extend(check_version_parity(plugin_versions))
    all_errors.extend(check_membership_parity(tool_members))
    all_errors.extend(check_readme_mentions(root, tool_members))
    return all_errors, summary


def main():
    print("Validating agent-plugins marketplace manifests...\n")

    all_errors, summary = validate_repo(ROOT)
    for line in summary:
        print(line)

    print()
    if all_errors:
        print(f"FAILED with {len(all_errors)} error(s):")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("PASSED: all marketplace manifests are valid.")
    return 0


# ---------------------------------------------------------------------------
# Self-test suite (--self-test) — builds throwaway fixture repos and asserts
# each check fires (and, for the clean fixture, that none do).
# ---------------------------------------------------------------------------

def _write_fixture(root, *, catalogs, manifests, readme=None):
    """Materialize a minimal marketplace repo under ``root``.

    ``catalogs`` maps a tool's marketplace path to its parsed-JSON content;
    ``manifests`` maps ``plugins/<dir>/<tool-manifest>`` paths to content.
    """
    for rel, data in {**catalogs, **manifests}.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    if readme is not None:
        (root / "README.md").write_text(readme, encoding="utf-8")


def _catalog(names):
    return {
        "name": "fixture-marketplace",
        "plugins": [{"name": n, "source": f"./plugins/{n}"} for n in names],
    }


def self_test():
    failures = []

    def expect(label, errors, *substrings):
        """Assert each substring appears in some error (or none exist)."""
        if not substrings:
            if errors:
                failures.append(f"{label}: expected no errors, got {errors}")
            return
        for sub in substrings:
            if not any(sub in err for err in errors):
                failures.append(f"{label}: no error containing {sub!r} in {errors}")

    claude_cat = Path(".claude-plugin/marketplace.json")
    cursor_cat = Path(".cursor-plugin/marketplace.json")
    codex_cat = Path(".agents/plugins/marketplace.json")

    def manifest_paths(name, version="1.0.0", tools=("claude", "cursor", "codex")):
        out = {}
        for tool in tools:
            rel = Path("plugins") / name / f".{tool}-plugin" / "plugin.json"
            out[rel] = {"name": name, "version": version}
        return out

    # 1. Clean fixture: three catalogs, one plugin, matching versions, README
    #    mention — every check must pass (the positive case).
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_fixture(root,
                       catalogs={claude_cat: _catalog(["alpha"]),
                                 cursor_cat: _catalog(["alpha"]),
                                 codex_cat: _catalog(["alpha"])},
                       manifests=manifest_paths("alpha"),
                       readme="# fixture\n\n- alpha: does things\n")
        errors, _ = validate_repo(root)
        expect("clean fixture", errors)

    # 2. Membership parity: registered for Claude only → Cursor catalog error.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_fixture(root,
                       catalogs={claude_cat: _catalog(["alpha"]),
                                 cursor_cat: _catalog([])},
                       manifests=manifest_paths("alpha"),
                       readme="alpha\n")
        errors, _ = validate_repo(root)
        expect("membership parity", errors,
               "[Cursor] plugin 'alpha'", "missing from this one")

    # 3. Version parity: differing semver across tools.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifests = manifest_paths("alpha", version="1.0.0", tools=("claude",))
        manifests.update(manifest_paths("alpha", version="1.1.0", tools=("cursor",)))
        _write_fixture(root,
                       catalogs={claude_cat: _catalog(["alpha"]),
                                 cursor_cat: _catalog(["alpha"])},
                       manifests=manifests,
                       readme="alpha\n")
        errors, _ = validate_repo(root)
        expect("version parity", errors, "mismatched versions across tools")

    # 4. Non-semver version string.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_fixture(root,
                       catalogs={claude_cat: _catalog(["alpha"]),
                                 cursor_cat: _catalog(["alpha"])},
                       manifests=manifest_paths("alpha", version="v1"),
                       readme="alpha\n")
        errors, _ = validate_repo(root)
        expect("semver", errors, "non-semver version 'v1'")

    # 5. Registered plugin with no directory on disk.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_fixture(root,
                       catalogs={claude_cat: _catalog(["ghost"]),
                                 cursor_cat: _catalog(["ghost"])},
                       manifests={},
                       readme="ghost\n")
        errors, _ = validate_repo(root)
        expect("missing dir", errors, "references missing directory: plugins/ghost/")

    # 6. README omission: valid everywhere, absent from README.md.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_fixture(root,
                       catalogs={claude_cat: _catalog(["alpha"]),
                                 cursor_cat: _catalog(["alpha"])},
                       manifests=manifest_paths("alpha"),
                       readme="# fixture marketplace\n\nnothing here\n")
        errors, _ = validate_repo(root)
        expect("readme mention", errors, "'alpha' is not mentioned in README.md")

    # 7. Source-path resolution, including the hidden-directory edge that
    #    lstrip("./") used to mangle (".hidden" would lose its leading dot).
    cases = [("./plugins/foo", "foo"), ("plugins/foo", "foo"), ("foo", "foo"),
             ("./.hidden-plugin", ".hidden-plugin")]
    for source, want in cases:
        got = _plugin_dir_name(source, "fallback")
        if got != want:
            failures.append(f"_plugin_dir_name({source!r}) = {got!r}, want {want!r}")
    if _plugin_dir_name({"source": "github", "repo": "x/y"}, "n") is not None:
        failures.append("_plugin_dir_name(remote) should be None")

    if failures:
        print(f"SELF-TEST FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("SELF-TEST PASSED: 7 scenario(s), all checks fire as expected.")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        sys.exit(self_test())
    sys.exit(main())

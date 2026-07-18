---
name: scaffold-plugin
description: Scaffold a new plugins/<name>/ directory with paired Claude Code + Cursor manifests at a valid, matching semver version, register it in both marketplace.json catalogs, and validate. Use when the user wants to add a new plugin to this marketplace.
disable-model-invocation: true
---

# Scaffold Plugin

Creates a new plugin directory and registers it in both marketplace catalogs, following
[docs/adding-a-plugin.md](../../../docs/adding-a-plugin.md). This has side effects (new files,
edited catalogs), so it's invoked deliberately via `/scaffold-plugin`, not automatically.

## Steps

1. Ask the user for: plugin name (lowercase kebab-case), display name, one-line description, and
   which tool(s) it targets (Claude Code, Cursor, or both).
2. Pick a starting `version`: `0.1.0` if the plugin isn't stable yet, `1.0.0` if it's launching
   stable. Use the **same value** in every manifest you create — see step 3.
3. Create `plugins/<name>/`:
   - `.claude-plugin/plugin.json` (if targeting Claude Code) — `name`, `description`, `version`,
     `author`, `license`.
   - `.cursor-plugin/plugin.json` (if targeting Cursor) — same fields plus `displayName` and
     `keywords`; `version` must be byte-identical to the Claude Code manifest.
   - `skills/<name>/SKILL.md` and/or `agents/<name>.md` stubs for whatever the plugin does.
   - `README.md` with install/usage instructions.
4. Register the plugin in `.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json`
   — same `name`, `source`, `description` in both (docs/adding-a-plugin.md §2). Marketplace
   entries don't carry their own `version`; the plugin manifest's `version` is what's checked.
5. Run `python3 scripts/validate_manifests.py` and report the result. If the plugin ships its own
   `scripts/validate.py`, run that too.
6. Remind the user of the versioning contract going forward: bump PATCH for fixes, MINOR for
   backward-compatible additions, MAJOR for breaking changes, and always update every manifest's
   `version` together — the validator rejects any mismatch between a plugin's Claude Code and
   Cursor manifests.

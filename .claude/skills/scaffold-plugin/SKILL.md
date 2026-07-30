---
name: scaffold-plugin
description: Scaffold a new plugins/<name>/ directory with paired Claude Code + Cursor + Codex manifests at a valid, matching semver version, register it in every marketplace.json catalog, and validate. Use when the user wants to add a new plugin to this marketplace.
disable-model-invocation: true
---

# Scaffold Plugin

Creates a new plugin directory and registers it in every marketplace catalog, following
[docs/adding-a-plugin.md](../../../docs/adding-a-plugin.md). This has side effects (new files,
edited catalogs), so it's invoked deliberately via `/scaffold-plugin`, not automatically.

## Steps

1. Ask the user for: plugin name (lowercase kebab-case), display name, one-line description, and
   which tool(s) it targets (Claude Code, Cursor, Codex, or any combination).
2. Pick a starting `version`: `0.1.0` if the plugin isn't stable yet, `1.0.0` if it's launching
   stable. Use the **same value** in every manifest you create — see step 3.
3. Create `plugins/<name>/`:
   - `.claude-plugin/plugin.json` (if targeting Claude Code) — `name`, `description`, `version`,
     `author`, `license`.
   - `.cursor-plugin/plugin.json` (if targeting Cursor) — same fields plus `displayName` and
     `keywords`; `version` must be byte-identical to the Claude Code manifest.
   - `.codex-plugin/plugin.json` (if targeting Codex) — `name`, `version`, `description`,
     `author`, `license`, plus an optional `interface: { displayName, shortDescription,
     category }`; `version` must be byte-identical to the other manifests.
   - `skills/<name>/SKILL.md` and/or `agents/<name>.md` stubs for whatever the plugin does.
   - `README.md` with install/usage instructions.
4. Register the plugin in every catalog it targets — `.claude-plugin/marketplace.json`,
   `.cursor-plugin/marketplace.json`, `.agents/plugins/marketplace.json` — same `name`, `source`,
   `description` in all of them (docs/adding-a-plugin.md §2). Codex's catalog entry also carries
   `policy: { installation: "AVAILABLE", authentication: "ON_INSTALL" }` and a `category`.
   Marketplace entries don't carry their own `version`; the plugin manifest's `version` is what's
   checked.
5. Run `python3 scripts/validate_manifests.py` and report the result. If the plugin ships its own
   `scripts/validate.py`, run that too.
6. Remind the user of the versioning contract going forward: bump PATCH for fixes, MINOR for
   backward-compatible additions, MAJOR for breaking changes, and always update every manifest's
   `version` together — the validator rejects any mismatch across a plugin's manifests.

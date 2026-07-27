# Adding a plugin

This repository is a multi-tool marketplace: a single plugin can be published
to **Claude Code**, **Cursor**, or both. Each plugin is a self-contained
directory under `plugins/`, and it must be registered in the marketplace
catalog of every tool it targets.

## 1. Create the plugin directory

Create `plugins/<plugin-name>/`, using a lowercase, kebab-case name (no
spaces). Inside it, add one manifest per tool you support:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # required for Claude Code support
└── .cursor-plugin/
    └── plugin.json          # required for Cursor support (if compatible)
```

### Claude Code manifest — `.claude-plugin/plugin.json`

`name` is the only required field. Bump `version` on each release so users
receive the update (omit it to let each git commit act as a new version).

```json
{
  "name": "<plugin-name>",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": { "name": "David Castillo", "email": "davcs86@gmail.com" },
  "license": "MIT"
}
```

### Cursor manifest — `.cursor-plugin/plugin.json`

Cursor's manifest schema is intentionally close to Claude Code's; `name` is
the only required field. Cursor discovers components (skills from `skills/`,
subagents from `agents/`, plus rules, commands, hooks, and MCP config) from
their default directories, or you can point at custom paths.

```json
{
  "name": "<plugin-name>",
  "displayName": "<Plugin Name>",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": { "name": "David Castillo", "email": "davcs86@gmail.com" },
  "license": "MIT",
  "keywords": ["utilities"]
}
```

#### One tree, two tools

Because Cursor's `skills/`+`agents/` layout, its `SKILL.md` frontmatter, and its
subagent `Task` tool all match Claude Code's, a plugin can serve **both tools
from a single component tree** — no per-tool copies. Write frontmatter as a
*union* of both tools' keys; each tool reads the keys it knows and ignores the
rest. `design-buddy` is the worked example:

- Skills keep Claude's `argument-hint`/`allowed-tools` (Cursor ignores them) and
  add `disable-model-invocation: true` (so Cursor treats them as manual `/skill`
  commands, matching Claude's slash-command UX).
- Agents keep `tools: …` for Claude and add `readonly: true` so Cursor enforces
  the same read-only contract.
- Cursor invokes commands flat (`/design`), without Claude's `plugin:` namespace,
  so keep skill names globally unique and phrase cross-references tool-neutrally.

## 2. Register it in both marketplace catalogs

Add an entry to the `plugins` array of each catalog. The `source` is the
plugin directory's repo-relative path, starting with `./` — the same form in
both catalogs, so the two stay consistent (and so a plugin that ships its own
integrity validator can resolve the entry):

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "description": "What the plugin does"
}
```

> A catalog can instead set `metadata.pluginRoot` (e.g. `"./plugins"`) and
> reference plugins by bare directory name. We keep explicit `./plugins/...`
> paths so both the Claude Code and Cursor catalogs read identically.

## 3. Keep it semver-compliant

`version` must be `MAJOR.MINOR.PATCH` (an optional `-prerelease` and/or
`+build` suffix is allowed) — that's what lets Claude Code and Cursor tell
users an update is available. Bump it on every release:

- **PATCH** (`1.0.0` → `1.0.1`) — bug fixes, wording tweaks, no behavior change
- **MINOR** (`1.0.1` → `1.1.0`) — backward-compatible additions (new skill,
  new optional field)
- **MAJOR** (`1.1.0` → `2.0.0`) — breaking changes (renamed/removed skill or
  command, changed required inputs)

Start a new plugin at `0.1.0` if it's not yet stable, or `1.0.0` if it is.

If a plugin ships both manifests, their `version` fields must be **exactly
identical** — `scripts/validate_manifests.py` fails the build on any
mismatch, since a stale version on one tool means that tool's users never see
the update.

## 4. Validate before committing

Run the validator (standard-library Python 3, no dependencies):

```shell
python3 scripts/validate_manifests.py
```

It fails if a registered plugin has no matching `plugins/<name>/` directory,
is missing the required manifest for that tool, or if any manifest is invalid
JSON or non-semver, including a version mismatch between a plugin's own
manifests. It also enforces **membership parity** (a plugin registered in one
catalog must be registered in every catalog) and requires every registered
plugin to be mentioned in the top-level `README.md` — so add your plugin to
the README's plugin table as part of the same change. CI runs the same checks
on every push and pull request, so a green local run means a green pipeline.

## 5. Commit

Commit the new plugin directory, both updated catalogs, and the README entry
together so the marketplace stays internally consistent.

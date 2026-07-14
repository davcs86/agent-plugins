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

## 3. Validate before committing

Run the validator (standard-library Python 3, no dependencies):

```shell
python3 scripts/validate_manifests.py
```

It fails if a registered plugin has no matching `plugins/<name>/` directory,
is missing the required manifest for that tool, or if any manifest is invalid
JSON. CI runs the same check on every push and pull request, so a green local
run means a green pipeline.

## 4. Commit

Commit the new plugin directory and both updated catalogs together so the
marketplace stays internally consistent.

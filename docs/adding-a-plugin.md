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

- Skills keep Claude's `argument-hint`/`allowed-tools` (Cursor ignores them).
- Agents keep `tools: …` for Claude and add `readonly: true` so Cursor enforces
  the same read-only contract.
- Cursor invokes commands flat (`/design-debate`), without Claude's `plugin:`
  namespace. Skill names must therefore be globally unique **and** must not shadow
  a host tool's built-in commands — Claude Code ships its own `/review`, and `plan`
  reads as plan mode, which is why design-buddy 2.0.0 renamed its three skills.
  Phrase cross-references tool-neutrally.

#### Deciding `disable-model-invocation`

`disable-model-invocation: true` (a Cursor key) makes a skill reachable **only** by
an explicit `/command`. That is the right default for a skill with side effects
outside its own artifact directory, and the wrong default for everything else: a
skill the model can never trigger is a skill nobody finds unless they already know
its name. Set it per skill, on this line:

- **Command-only** — the skill writes into files the user did not point it at, or
  mutates external state. `context-constitution` prepends to the host's `CLAUDE.md`;
  `backtest` mutates strategies on a live trading backend. Both keep the key.
- **Model-invocable** — the skill's default mode only reads, or writes solely into
  its own configured artifact directory, behind a gate. `design-debate`, `impl-plan`,
  `plan-review` and `context-scrubber` drop the key.

A model-invocable skill whose deeper modes *do* have side effects must state the
restriction in its own body: when it was triggered implicitly rather than by an
explicit command, it runs its read-only mode and asks before anything else.

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

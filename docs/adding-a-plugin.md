# Adding a plugin

This repository is a multi-tool marketplace: a single plugin can be published
to **Claude Code**, **Cursor**, **Codex**, or any combination. Each plugin is
a self-contained directory under `plugins/`, and it must be registered in the
marketplace catalog of every tool it targets.

## 1. Create the plugin directory

Create `plugins/<plugin-name>/`, using a lowercase, kebab-case name (no
spaces). Inside it, add one manifest per tool you support:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # required for Claude Code support
├── .cursor-plugin/
│   └── plugin.json          # required for Cursor support (if compatible)
└── .codex-plugin/
    └── plugin.json          # required for Codex support (if compatible)
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

### Codex manifest — `.codex-plugin/plugin.json`

`name`, `version`, and `description` are required. Codex discovers `skills/` and
`agents/` from their default directories automatically (no manifest field needed
for either), or you can point at a custom skills path with `"skills": "./skills/"`.
An optional `interface` sub-object carries `displayName`, `shortDescription`, and
`category` for Codex's install surfaces.

```json
{
  "name": "<plugin-name>",
  "version": "1.0.0",
  "description": "What the plugin does",
  "author": { "name": "David Castillo", "email": "davcs86@gmail.com" },
  "license": "MIT",
  "keywords": ["utilities"],
  "skills": "./skills/",
  "interface": {
    "displayName": "<Plugin Name>",
    "shortDescription": "One-line summary",
    "category": "Productivity"
  }
}
```

#### One tree, every tool

Because Cursor's and Codex's `skills/`+`agents/` layout, `SKILL.md` frontmatter, and
subagent conventions all match Claude Code's, a plugin can serve **every tool from a
single component tree** — no per-tool copies. Write frontmatter as a *union* of every
tool's keys; each tool reads the keys it knows and ignores the rest. `design-buddy` is
the worked example:

- Skills keep Claude's `argument-hint`/`allowed-tools` (Cursor and Codex ignore them).
- Agents keep `tools: …` for Claude and add `readonly: true` so Cursor enforces
  the same read-only contract. Codex has no agent-manifest equivalent yet — it
  discovers `agents/*.md` the same way, but doesn't read either key.
- Codex's SKILL.md support only reads `name` and `description` from frontmatter, so
  it never needs anything added for its sake — the union built for Claude and Cursor
  already covers it.
- Cursor and Codex both invoke commands flat (`/design-debate`), without Claude's
  `plugin:` namespace. Skill names must therefore be globally unique **and** must not
  shadow a host tool's built-in commands — Claude Code ships its own `/review`, and
  `plan` reads as plan mode, which is why design-buddy 2.0.0 renamed its three skills.
  Phrase cross-references tool-neutrally.

#### Deciding `disable-model-invocation`

`disable-model-invocation: true` (a Cursor key) makes a skill reachable **only** by
an explicit `/command`. That is the right default for a skill with side effects
outside its own artifact directory, and the wrong default for everything else: a
skill the model can never trigger is a skill nobody finds unless they already know
its name. Set it per skill, on this line. (Codex's SKILL.md frontmatter has no
equivalent key today — command-only skills are Cursor-only enforcement for now.)

- **Command-only** — the skill writes into files the user did not point it at, or
  mutates external state. `context-constitution` prepends to the host's `CLAUDE.md`;
  `backtest` mutates strategies on a live trading backend. Both keep the key.
- **Model-invocable** — the skill's default mode only reads, or writes solely into
  its own configured artifact directory, behind a gate. `design-debate`, `impl-plan`,
  `plan-review` and `context-scrubber` drop the key.

A model-invocable skill whose deeper modes *do* have side effects must state the
restriction in its own body: when it was triggered implicitly rather than by an
explicit command, it runs its read-only mode and asks before anything else.

## 2. Register it in every marketplace catalog

Add an entry to the `plugins` array of each catalog — `.claude-plugin/marketplace.json`,
`.cursor-plugin/marketplace.json`, and `.agents/plugins/marketplace.json` for Codex.
The `source` is the plugin directory's repo-relative path, starting with `./` — the
same form in every catalog, so they stay consistent (and so a plugin that ships its
own integrity validator can resolve the entry):

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "description": "What the plugin does"
}
```

> A catalog can instead set `metadata.pluginRoot` (e.g. `"./plugins"`) and
> reference plugins by bare directory name. We keep explicit `./plugins/...`
> paths so every catalog reads identically.

Codex's catalog entries also carry a `policy` block and `category` (its install
surfaces use them; the validator doesn't require them, but the real Codex CLI does):

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "description": "What the plugin does",
  "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
  "category": "Productivity"
}
```

Codex's catalog also has different top-level required fields than Claude Code's and
Cursor's — `interface.displayName` instead of `owner`:

```json
{
  "name": "davcs86-agent-plugins",
  "interface": { "displayName": "David Castillo's Agent Plugins" },
  "plugins": [ /* entries as above */ ]
}
```

## 3. Keep it semver-compliant

`version` must be `MAJOR.MINOR.PATCH` (an optional `-prerelease` and/or
`+build` suffix is allowed) — that's what lets every tool tell
users an update is available. Bump it on every release:

- **PATCH** (`1.0.0` → `1.0.1`) — bug fixes, wording tweaks, no behavior change
- **MINOR** (`1.0.1` → `1.1.0`) — backward-compatible additions (new skill,
  new optional field)
- **MAJOR** (`1.1.0` → `2.0.0`) — breaking changes (renamed/removed skill or
  command, changed required inputs)

Start a new plugin at `0.1.0` if it's not yet stable, or `1.0.0` if it is.

If a plugin ships more than one manifest, their `version` fields must be
**exactly identical** — `scripts/validate_manifests.py` fails the build on any
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

Commit the new plugin directory, every updated catalog, and the README entry
together so the marketplace stays internally consistent.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **multi-tool agent plugin marketplace**: one repository that catalogs plugins for
several AI coding agents (Claude Code and Cursor today; Codex and others planned).
There is no application to build or run — the deliverable is a set of JSON manifests
plus the plugin component trees they point at, kept internally consistent by a
standard-library Python validator.

## Commands

```shell
# Validate every marketplace catalog + plugin manifest (the primary check)
python3 scripts/validate_manifests.py

# Run the marketplace validator's own fixture-based test suite
python3 scripts/validate_manifests.py --self-test

# Run a single plugin's own integrity validator
python3 plugins/<plugin-name>/scripts/validate.py

# Run that validator's built-in unit tests (validators ship their own test suite)
python3 plugins/<plugin-name>/scripts/validate.py --self-test
```

CI (`.github/workflows/validate.yml`) runs `validate_manifests.py --self-test` then
`validate_manifests.py`, then for every
`plugins/*/scripts/validate.py` runs `--self-test` followed by the validator itself.
A green local run of those same commands means a green pipeline. There is no build,
lint, or package step; **all tooling is Python 3 stdlib only** (no `pip install`,
no dependencies) — preserve that when adding scripts.

## Architecture

The repo is organized around one core invariant: **the same plugin set is published
to multiple tools, and every tool's view of it must stay in lockstep.** Three things
enforce that:

- **Parallel catalogs.** Each tool has its own top-level marketplace catalog
  (`.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`). They are
  deliberately kept structurally identical — same `plugins` entries, same explicit
  `./plugins/<name>` source paths — so the two read the same. Adding/removing a
  plugin means editing **both** catalogs together.

- **Per-tool plugin manifests with locked versions.** Each plugin lives in
  `plugins/<name>/` and ships one manifest per tool it targets
  (`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`). When a plugin ships
  more than one, their `version` fields must be **byte-identical** semver — a
  mismatch means one tool's users never see the update, and the validator fails the
  build on it. Bump the version in every manifest at once.

- **One component tree, two tools.** A plugin's `skills/` + `agents/` tree is shared,
  not duplicated per tool. Frontmatter is written as a *union* of both tools' keys
  (e.g. skills keep Claude's `argument-hint`/`allowed-tools`; agents keep `tools:` and
  add Cursor's `readonly: true`) — each tool reads the keys it knows and ignores the
  rest. Cursor's `disable-model-invocation: true` is set **per skill, not by default**:
  it makes a skill reachable only by explicit command, so it is right for a skill with
  side effects outside its own artifact dir (`context-constitution`, `backtest`) and
  wrong for one the model should be able to trigger. See `docs/adding-a-plugin.md`.
  Cursor invokes commands
  flat (`/design-debate`) without Claude's `plugin:` namespace, so skill names must be
  globally unique **and** must not collide with a host tool's built-in commands — that
  is why design-buddy 2.0.0 renamed `design`/`plan`/`review` to
  `design-debate`/`impl-plan`/`plan-review`. Phrase cross-references tool-neutrally.

**Extending to a new agent tool** is intentionally a one-place change: append an entry
to the `TOOLS` list in `scripts/validate_manifests.py` (its `marketplace` path and the
`plugin_manifest` each plugin must ship). The validator then enforces the same
existence/semver/parity rules for the new tool automatically.

### Validation is the backbone

`scripts/validate_manifests.py` is the source of truth for repo integrity. It checks
each catalog is valid JSON with required fields, that every registered plugin resolves
to a real `plugins/<name>/` directory containing that tool's manifest, that each
`version` is valid `MAJOR.MINOR.PATCH` semver, that versions match across a
plugin's manifests, that every catalog registers the **same plugin set** (membership
parity — a plugin added to one catalog but not the others fails the build), and that
every registered plugin is mentioned in the top-level `README.md` (so a new plugin
can't ship undocumented). Remote (github/git) plugin sources are skipped — only local
`./plugins/...` sources are checked against the on-disk tree. The script carries its
own `--self-test` fixture suite, same as the per-plugin validators.

Two automation layers wrap it so mistakes surface early:
- **PostToolUse hook** (`.claude/settings.json` → `scripts/hooks/validate_on_edit.py`):
  after any `Edit`/`Write` to a `*-plugin/(marketplace|plugin).json` file, it reruns
  `validate_manifests.py` and, for edits inside a plugin dir, that plugin's own
  `scripts/validate.py`. It exits non-zero to block on failure — fix before committing.
- **CI** runs the same checks on every push and PR.

Individual plugins may ship their own `scripts/validate.py` that validates deeper,
plugin-specific structure and carries a `--self-test` suite; these are independent of
the marketplace validator and run separately in CI.

## Repo-local Claude tooling

`.claude/` configures this repo's own Claude Code sessions (distinct from the plugins
being published): the PostToolUse validation hook, a read-only `manifest-parity-reviewer`
agent (audits manifest/semver/catalog consistency before merging), and a
`scaffold-plugin` skill (`/scaffold-plugin`) that scaffolds a new plugin and registers
it in both catalogs. `.mcp.json` wires up a project-scoped GitHub MCP server.

## Adding or changing a plugin

Follow `docs/adding-a-plugin.md`. In short: create `plugins/<name>/` with a manifest
per tool, register an identical entry in **both** marketplace catalogs, keep versions
semver and identical across a plugin's manifests, and run `validate_manifests.py`
before committing. Commit the plugin directory and both catalog edits together so the
marketplace is never left inconsistent. `/scaffold-plugin` automates the scaffolding.

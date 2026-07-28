# agent-plugins

A personal, multi-tool **agent plugin marketplace**. One repository that
catalogs plugins for several AI coding agents, each described by its own
marketplace manifest so the same plugin set can be published to multiple
tools.

## Supported tools

| Tool            | Marketplace catalog                 | Status          |
| --------------- | ----------------------------------- | --------------- |
| **Claude Code** | `.claude-plugin/marketplace.json`   | Supported       |
| **Cursor**      | `.cursor-plugin/marketplace.json`   | Supported       |
| Codex, others   | —                                   | Planned         |

> The structure is deliberately tool-agnostic. Adding a future agent (Codex,
> etc.) means adding its `*-plugin/marketplace.json` catalog and a matching
> entry in `scripts/validate_manifests.py` — no restructuring required.

## Plugins

| Plugin | Tools | Description |
| ------ | ----- | ----------- |
| [`design-buddy`](plugins/design-buddy/) | Claude Code · Cursor | A repo-agnostic design partner: adversarially debated designs, evidence-grounded implementation plans, and a strict plan-review gate — from bug fixes to rearchitectures. |
| [`context-forge`](plugins/context-forge/) | Claude Code · Cursor | A context-engineering toolkit: `context-constitution` extracts a repo's hidden patterns, cross-module contracts, and git-history scars into an evidence-cited `context-constitution.md` and behavioral contract; `context-scrubber` audits the repo's context files and reports every line that fails the litmus test — stale citations, restated facts, duplication, contradictions, bloat — with an optional gated trim. |
| [`strat-lab`](plugins/strat-lab/) | Claude Code · Cursor | A backtesting workbench for the xstockstrat MCP server: ensures data coverage (backfill), runs strategy backtests, survives over-token-limit diagnostics by saving-and-parsing, aggregates an independent-per-symbol basket, and self-grills results against a pre-change oracle before trusting them. |

Every plugin ships one shared `skills/` + `agents/` tree with a manifest for
each tool. Subagents run through the same `Task` tool on both Claude Code
and Cursor, so each plugin is registered in both catalogs.

## Add this marketplace to your agent

### Claude Code

```shell
/plugin marketplace add davcs86/agent-plugins
/plugin install <plugin-name>@davcs86-agent-plugins
```

You can also add it from a local checkout:

```shell
/plugin marketplace add ./agent-plugins
```

### Cursor

Point Cursor at this repository's Cursor catalog
(`.cursor-plugin/marketplace.json`) as a marketplace source, then install
individual plugins from it. See the
[Cursor plugins documentation](https://cursor.com/docs/plugins) for the
current add-a-marketplace flow.

## Repository structure

```
agent-plugins/
├── .claude-plugin/
│   └── marketplace.json     # Claude Code marketplace catalog
├── .cursor-plugin/
│   └── marketplace.json     # Cursor marketplace catalog
├── .claude/
│   ├── settings.json         # PostToolUse hook: re-validate manifests on edit
│   ├── agents/
│   │   └── manifest-parity-reviewer.md  # read-only manifest/semver auditor
│   └── skills/
│       └── scaffold-plugin/  # scaffolds a new plugin + registers it
├── .mcp.json                 # project-scoped GitHub MCP server
├── plugins/                  # individual plugins live here, one dir each
├── docs/
│   └── adding-a-plugin.md    # how to add + register a new plugin
├── scripts/
│   ├── validate_manifests.py # validates every marketplace manifest (CI)
│   └── hooks/
│       └── validate_on_edit.py  # the PostToolUse hook's implementation
└── .github/workflows/
    └── validate.yml          # runs the validator on push / PR
```

To add another plugin, see [docs/adding-a-plugin.md](docs/adding-a-plugin.md)
— or run `/scaffold-plugin` in Claude Code to have it scaffolded for you.

## Validate locally

The validator is standard-library Python 3 (no dependencies):

```shell
python3 scripts/validate_manifests.py
```

It confirms each marketplace manifest is valid JSON, that every registered
plugin resolves to a real `plugins/<name>/` directory with the required
manifest, that every plugin manifest's `version` is valid semver and
identical across every tool the plugin targets, that every catalog registers
the **same plugin set** (membership parity), and that every registered plugin
is listed in this README. Run `python3 scripts/validate_manifests.py
--self-test` to execute its built-in fixture tests. CI runs the same checks
on every push and pull request, and a `.claude/settings.json` hook reruns
them automatically whenever a manifest is edited in a Claude Code session.

## License

[MIT](LICENSE) © 2026 David Castillo

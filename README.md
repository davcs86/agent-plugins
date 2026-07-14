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

`design-buddy` ships one shared `skills/` + `agents/` tree with a manifest for
each tool. Its subagents run through the same `Task` tool on both Claude Code
and Cursor, so it is registered in both catalogs.

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
├── plugins/                 # individual plugins live here, one dir each
├── docs/
│   └── adding-a-plugin.md    # how to add + register a new plugin
├── scripts/
│   └── validate_manifests.py # validates every marketplace manifest (CI)
└── .github/workflows/
    └── validate.yml          # runs the validator on push / PR
```

To add another plugin, see [docs/adding-a-plugin.md](docs/adding-a-plugin.md).

## Validate locally

The validator is standard-library Python 3 (no dependencies):

```shell
python3 scripts/validate_manifests.py
```

It confirms each marketplace manifest is valid JSON and that every registered
plugin resolves to a real `plugins/<name>/` directory with the required
manifest. CI runs the same check on every push and pull request.

## License

[MIT](LICENSE) © 2026 David Castillo

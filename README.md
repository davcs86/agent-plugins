# agent-tooling

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

## Add this marketplace to your agent

### Claude Code

```shell
/plugin marketplace add davcs86/agent-tooling
/plugin install <plugin-name>@agent-tooling
```

You can also add it from a local checkout:

```shell
/plugin marketplace add ./agent-tooling
```

### Cursor

Point Cursor at this repository's Cursor catalog
(`.cursor-plugin/marketplace.json`) as a marketplace source, then install
individual plugins from it. See the
[Cursor plugins documentation](https://cursor.com/docs/plugins) for the
current add-a-marketplace flow.

## Repository structure

```
agent-tooling/
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

No plugins are published yet — the catalogs start empty. To add one, see
[docs/adding-a-plugin.md](docs/adding-a-plugin.md).

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

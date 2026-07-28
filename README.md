# agent-plugins

Plugins that make a coding agent **show its work**: debate a design before writing
code, ground every plan step in a real `path:line`, and keep a repo's agent-context
files honest. Published to **Claude Code** and **Cursor** from one shared source tree,
with every manifest version-locked and parity-checked in CI.

```shell
# Claude Code
/plugin marketplace add davcs86/agent-plugins
/plugin install context-forge@davcs86-agent-plugins
```

Cursor: add this repo as a marketplace source (see
[Cursor plugins docs](https://cursor.com/docs/plugins)), then install from it.

## The plugins

### [`context-forge`](plugins/context-forge/) — context engineering

Two halves of the same job: put the knowledge an agent actually needs into your
context files, and get everything else out.

| Skill | Use it when |
|---|---|
| **`context-constitution`** | You're writing or bootstrapping a `CLAUDE.md`/`AGENTS.md`, onboarding an agent to an inherited codebase, or the agent keeps making the same mistake because a convention was never written down. Produces an evidence-cited `context-constitution.md` where every rule cites a `path:line` or a commit — nothing invented. |
| **`context-scrubber`** | Your `CLAUDE.md` has grown past the point of usefulness. Reports every line that costs tokens on each load without changing how the agent behaves — citations that no longer resolve, facts the agent reads for free, rules duplicated across files, claims the code now contradicts. Read-only by default; trimming is separately gated. |

**See the actual output** — both skills run against this very repository:
[`examples/`](examples/).

### [`design-buddy`](plugins/design-buddy/) — design before code

A three-stage pipeline you can enter at any stage.

| Skill | Use it when |
|---|---|
| **`design-debate`** | You know *what* to change but not *how*. Recons the repo, then runs a mediated proposer-vs-adversary debate — scaled from one round for a bug fix to a multi-angle panel for a rearchitecture — and writes a design doc recording the chosen approach **and the alternatives that lost**. |
| **`impl-plan`** | You have a decided approach and want numbered, executable steps. Every step cites evidence found by grep or read; verification commands come from your repo's own harness, not an assumed one. |
| **`plan-review`** | Before anyone executes the plan. A read-only reviewer checks each step's evidence still resolves, the design is honored, and no host hard rule is violated, then records a binding verdict in the plan. Blockers cannot be waived. |

### [`strat-lab`](plugins/strat-lab/) — backtesting workbench

| Skill | Use it when |
|---|---|
| **`backtest`** | You want to backtest, sweep a parameter, or reproduce a strategy report's numbers. Handles the three ways the naive path fails silently: oversized diagnostics, sequential-vs-independent basket aggregation, and a mutated strategy returning garbage. |

> **Requires the xstockstrat MCP server.** Unlike the other two,
> this plugin is not repo-agnostic — without that server connected it has nothing to
> call. Skip it unless you already run xstockstrat.

## What you get, concretely

Both context-forge skills were run against this repository, and the results are
committed as-is:

| File | What it is |
|---|---|
| [`examples/context-constitution.md`](examples/context-constitution.md) | This repo's own forged constitution — its Floor/Rules/Norms, each cited to a `path:line` or a commit |
| [`examples/context-constitution-findings.md`](examples/context-constitution-findings.md) | The defects the scan surfaced (two latent bugs and a doc-lie), routed out of the constitution for triage |
| [`examples/context-scrubber-findings.md`](examples/context-scrubber-findings.md) | The scrub report on this repo's own `CLAUDE.md` and `README.md` |

They are a dated snapshot, not generated output — see [`examples/README.md`](examples/README.md).

## How this repo publishes to two tools

The same plugin set ships to Claude Code and Cursor, and every tool's view of it stays
in lockstep. Each tool gets its own catalog (`.claude-plugin/marketplace.json`,
`.cursor-plugin/marketplace.json`) registering the same plugins, and each plugin ships
one manifest per tool with a byte-identical `version`. The `skills/` + `agents/` tree
is shared, not duplicated: frontmatter is a union of both tools' keys, and each tool
reads the ones it knows.

| Tool            | Marketplace catalog                 | Status    |
| --------------- | ----------------------------------- | --------- |
| **Claude Code** | `.claude-plugin/marketplace.json`   | Supported |
| **Cursor**      | `.cursor-plugin/marketplace.json`   | Supported |
| Codex, others   | —                                   | Planned   |

Adding a future agent means adding its `*-plugin/marketplace.json` catalog and one
entry in `scripts/validate_manifests.py` — no restructuring.

`scripts/validate_manifests.py` (stdlib-only Python 3, no dependencies) enforces all of
it: valid catalogs, every registered plugin resolving to a real directory with that
tool's manifest, semver versions matching across a plugin's manifests, the same plugin
set in every catalog, and every plugin documented in this README. CI runs it on every
push and PR; a `.claude/settings.json` hook reruns it whenever a manifest is edited.

```shell
python3 scripts/validate_manifests.py             # the marketplace
python3 scripts/validate_manifests.py --self-test # its own fixture suite
```

To add a plugin, see [docs/adding-a-plugin.md](docs/adding-a-plugin.md) — or run
`/scaffold-plugin` in Claude Code.

## Repository structure

```
agent-plugins/
├── .claude-plugin/marketplace.json   # Claude Code marketplace catalog
├── .cursor-plugin/marketplace.json   # Cursor marketplace catalog
├── .claude/                          # this repo's own Claude Code config
│   ├── settings.json                 #   PostToolUse hook: re-validate on manifest edit
│   ├── agents/manifest-parity-reviewer.md
│   └── skills/scaffold-plugin/       #   scaffolds a new plugin + registers it
├── .mcp.json                         # project-scoped GitHub MCP server
├── plugins/                          # one directory per plugin
├── examples/                         # context-forge output, run against this repo
├── docs/adding-a-plugin.md
├── scripts/
│   ├── validate_manifests.py
│   └── hooks/validate_on_edit.py
└── .github/workflows/validate.yml
```

## License

[MIT](LICENSE) © 2026 David Castillo

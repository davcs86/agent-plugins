# constitution-forge

A repo-agnostic **constitution builder**. It reads a repository the way a careful new hire would —
its docs, its CI, its lint and branch and migration setup — and turns the rules already *implied*
there into two durable artifacts:

1. a **`constitution.md`** — the repo's rules, deduped and ranked into ID'd tiers (Floor / Rules /
   Norms), every rule citing the `path:line` where it already lives; and
2. a **behavioral contract** prepended to the repo's **`CLAUDE.md`** — four repo-agnostic behaviors
   that shape *how* an agent works, pointing into the constitution IDs that enforce each.

The premise (from the "4-line CLAUDE.md" argument): agents fail on **behavior**, not capability.
So put behaviors up top where they shape how the agent thinks, keep facts in the constitution where
they belong, and **invent nothing** — every rule traces to a citation.

## What it does

- **Scans** the repo with a read-only subagent (`convention-scout`): module map, stated hard rules,
  CI-enforced checks, encoded conventions, test harness — each a `path:line` citation.
- **Synthesizes** an evidence-cited `constitution.md`: rules grouped into Floor / Rules / Norms,
  with anything unproven quarantined under `## Candidate rules (unverified)` instead of asserted.
- **Prepends** the four-behavior contract to `CLAUDE.md`, idempotently (sentinel-wrapped, so a
  re-run updates in place instead of stacking a second copy).
- **Handles monorepos**: one constitution + contract **per module**, then a **repo-wide** pass at
  the root. Repo-wide rules live once at the root; module constitutions stay thin and inherit.

## Usage

```shell
/constitution              # full flow: scan → synthesize → (gated) write
/constitution scan         # dry run — present artifacts inline, write nothing
/constitution write        # explicit full flow (same as no argument)
/constitution scan apps/web  # scope the analysis to one subdirectory
```

First run in a repo asks two questions (where to write each `constitution.md`, and whether the
contract should cite the generated IDs) and saves them to `.agents/constitution-forge.json`.
Everything is gated: nothing is written before you approve the synthesized result, and `scan` mode
never writes at all.

## Design

Single orchestrator (the skill) owns every write and every gate; the subagent is advisory and
read-only. The skill holds itself to its own Floor + Norms — see
[`skills/constitution/reference/principles.md`](skills/constitution/reference/principles.md) — the
first of which is **never invent a rule**. Progressive disclosure keeps the router
([`SKILL.md`](skills/constitution/SKILL.md)) small; protocol detail loads only when its phase runs.

## Compatibility

Ships one shared `skills/` + `agents/` tree with a manifest for each tool, so it runs on **Claude
Code** and **Cursor**. In Claude Code the gates use `AskUserQuestion`; under Cursor the skill asks
the same questions in plain chat.

## License

[MIT](../../LICENSE) © 2026 David Castillo

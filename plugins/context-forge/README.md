# context-forge

A repo-agnostic **tribal-knowledge extractor**. It analyzes a repository the way a senior engineer
onboarding a new hire would — not to recite the docs, but to warn about the things that aren't
written down — and turns that into two durable artifacts:

1. a **`context-constitution.md`** — the repo's *non-obvious* invariants: undocumented patterns it follows
   across many files, asymmetries (the one file that breaks a pattern), implicit cross-module
   contracts, and scars (*why* something is the way it is), grouped into ID'd tiers (Floor / Rules /
   Norms) and grounded in real evidence (multi-site citations, an authoritative site, or a commit);
   and
2. a **behavioral contract** prepended to the **root `CLAUDE.md`** — four repo-agnostic behaviors that
   shape *how* an agent works (root only, since `CLAUDE.md` loads root-down and the block is generic);
   plus a one-line **constitution pointer** in every `CLAUDE.md` so the constitution is actually
   discoverable (only `CLAUDE.md` is auto-loaded).

The premise: agents rarely fail for lack of capability — they fail on **behavior**, and they waste
time and tokens rediscovering, or missing, the patterns nobody wrote down. So put behaviors up top,
and fill the constitution with exactly the knowledge an agent would **miss on a normal read**. The value of any line is inversely proportional to how easily an agent would find it
alone; a rule already in the docs or CI is a one-line pointer, not a restatement.

## What it does

- **Scans** the repo with a read-only subagent (`convention-scout`) that hunts the non-obvious:
  emergent multi-site patterns (each with the *wrong default* it prevents), asymmetries, implicit
  cross-module contracts, and "looks-wrong-but-intentional" flags — every finding grounded in
  `path:line` evidence.
- **Mines git history** for scars — reverts, hotfixes, "fix: … because …" — to recover the *why*
  the code alone can't show, cited to commits/PRs.
- **Asks you** about anything that looks wrong but appears intentional, and records your answer as
  the rule's rationale — the only reliable way to capture true tribal knowledge.
- **Synthesizes** an evidence-cited `context-constitution.md` (Floor / Rules / Norms + a `Gotchas & scars`
  section), applying an inclusion test — *would an agent miss this on a normal read?* — so restated
  docs become one-line pointers and anything unproven is quarantined under `## Candidate rules
  (unverified)`.
- **Never drops what it found.** Things the scan surfaces that are *defects to fix* rather than
  *invariants to respect* — **documentation that lies** (behavior/config the docs promise but the code
  lacks), latent bugs, dead code — go into a sibling `context-constitution-findings.md` log, cited and with a
  suggested action, for triage. A defect is recorded, never frozen into a governance rule; and nothing
  grounded is silently discarded.
- **Prepends** the four-behavior contract to the **root** `CLAUDE.md` (not duplicated per module), and
  adds a **constitution pointer** to every `CLAUDE.md` so the constitution is discoverable — both
  idempotently sentinel-wrapped, so a re-run updates in place instead of stacking a copy.
- **Handles monorepos**: one constitution + contract **per module**, then a **repo-wide** pass at
  the root whose special focus is the cross-module contracts. Repo-wide rules live once at the root;
  module constitutions stay thin and inherit.

### Optional: library-doc cross-referencing

If **any** documentation-lookup MCP tool — one that resolves a package name and returns its docs,
[Context7](https://github.com/upstash/context7) being the reference example — is available in your
session, the skill uses it to sharpen the inclusion test for third-party-library usage: a setting
that **deviates** from the library's documented default is kept as a rule (a deliberate choice worth
capturing), while usage that just **matches the docs** is dropped or demoted to a pointer (an agent
can look it up). The skill matches on capability, not a fixed server name, so it works whether the
tool is user-configured (`mcp__<server>__…`) or plugin-bundled (`mcp__plugin_…__…`). This is a pure
enhancement — with no such tool available the skill falls back to consistency-based judgment and runs
unchanged. To enable Context7 specifically, add it to your host repo's MCP config, e.g.:

```json
{
  "mcpServers": {
    "Context7": { "type": "http", "url": "https://mcp.context7.com/mcp" }
  }
}
```

(See the Context7 docs for the current URL and any API-key requirement.)

## Usage

```shell
/context-constitution              # full flow: scan → synthesize → (gated) write
/context-constitution scan         # dry run — present artifacts inline, write nothing
/context-constitution write        # explicit full flow (same as no argument)
/context-constitution scan apps/web  # scope the analysis to one subdirectory
/context-constitution refresh      # incremental: re-derive only what changed since each target's baseline
/context-constitution refresh apps/web  # refresh just one target, from its own baseline
/context-constitution refresh check     # CI/linter: report drift, write nothing
```

**Refresh vs. write.** `write` forges from a full scan. `refresh` is the keep-it-current mode: it
diffs each target from **git** — the last commit that wrote that target's `context-constitution.md`, so a
scoped write to one module never throws off another's baseline and a **manual edit** to a constitution
is respected like any other commit — re-derives only the changed areas, flags rules whose citations
went stale, and applies the approved deltas without re-emitting unchanged rules. No baseline is stored
anywhere; git is the source of truth. `refresh … check` reports drift and writes nothing, so it is
safe to run in CI or on a schedule.

First run in a repo asks two questions (where to write each `context-constitution.md`, and whether the
contract should cite the generated IDs) and saves them to `.agents/context-forge.json`.
Everything is gated: nothing is written before you approve the synthesized result, and `scan` mode
never writes at all.

## Design

Single orchestrator (the skill) owns every write and every gate; the subagent is advisory and
read-only. The skill holds itself to its own Floor + Norms — see
[`skills/context-constitution/reference/principles.md`](skills/context-constitution/reference/principles.md) — the
first of which is **never invent a rule**. Progressive disclosure keeps the router
([`SKILL.md`](skills/context-constitution/SKILL.md)) small; protocol detail loads only when its phase runs.

## Compatibility

Ships one shared `skills/` + `agents/` tree with a manifest for each tool, so it runs on **Claude
Code** and **Cursor**. In Claude Code the gates use `AskUserQuestion`; under Cursor the skill asks
the same questions in plain chat.

## License

[MIT](../../LICENSE) © 2026 David Castillo

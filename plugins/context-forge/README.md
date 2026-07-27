# context-forge

A repo-agnostic **context-engineering toolkit** for AI coding agents — two complementary skills that
manage the context an agent loads from a repo. One **adds** the high-signal knowledge an agent would
miss; the other **removes** the low-signal content that just costs tokens:

- **`/context-constitution`** — a tribal-knowledge *extractor*. It analyzes a repo the way a senior
  engineer onboarding a new hire would — not to recite the docs, but to warn about the things nobody
  wrote down — and forges an evidence-cited `context-constitution.md` plus a behavioral contract in
  `CLAUDE.md`.
- **`/context-scrubber`** — the *inverse*: a context auditor. It reads the repo's already-loaded
  context files and reports every line that **fails the litmus test** — stale citations, restated
  facts, cross-file duplication, contradicted-by-code claims, and bloat — with an optional gated trim.

Both run on the same premise and the same litmus test: *the value of a context line is inversely
proportional to how easily an agent would find it alone.* `context-constitution` keeps only what an
agent would **miss**; `context-scrubber` flags what an agent would **find for free**. Both are single
orchestrators that own every write and every gate, spawn only read-only advisory subagents, and never
invent — every rule and every verdict is grounded in `path:line` evidence. They share one config file
(`.agents/context-forge.json`) and one governance set (`CF-*` Floor rules, `CF-N*` Norms).

## `/context-constitution` — forge the high-signal context

Turns a repo's non-obvious knowledge into two durable artifacts:

1. a **`context-constitution.md`** — the repo's *non-obvious* invariants: undocumented patterns it
   follows across many files, asymmetries (the one file that breaks a pattern), implicit cross-module
   contracts, and scars (*why* something is the way it is), grouped into ID'd tiers (Floor / Rules /
   Norms) and grounded in real evidence (multi-site citations, an authoritative site, or a commit);
2. a **behavioral contract** prepended to the **root `CLAUDE.md`** — four repo-agnostic behaviors that
   shape *how* an agent works (root only, since `CLAUDE.md` loads root-down and the block is generic);
   plus a one-line **constitution pointer** in every `CLAUDE.md` so the constitution is actually
   discoverable (only `CLAUDE.md` is auto-loaded).

- **Scans** the repo with a read-only subagent (`convention-scout`) that hunts the non-obvious:
  emergent multi-site patterns (each with the *wrong default* it prevents), asymmetries, implicit
  cross-module contracts, and "looks-wrong-but-intentional" flags — every finding grounded in
  `path:line` evidence.
- **Mines git history** for scars — reverts, hotfixes, "fix: … because …" — to recover the *why*
  the code alone can't show, cited to commits/PRs.
- **Asks you** about anything that looks wrong but appears intentional, and records your answer as
  the rule's rationale — the only reliable way to capture true tribal knowledge.
- **Never drops what it found.** Defects to *fix* rather than invariants to *respect* — **documentation
  that lies**, latent bugs, dead code — go into a sibling `context-constitution-findings.md` log, cited
  and with a suggested action, for triage; nothing grounded is silently discarded.
- **Handles monorepos**: one constitution + contract **per module**, then a **repo-wide** pass at the
  root whose special focus is the cross-module contracts. Repo-wide rules live once at the root.

```shell
/context-constitution              # full flow: scan → synthesize → (gated) write
/context-constitution scan         # dry run — present artifacts inline, write nothing
/context-constitution scan apps/web  # scope the analysis to one subdirectory
/context-constitution refresh      # incremental: re-derive only what changed since each target's baseline
/context-constitution refresh check  # CI/linter: report drift, write nothing
```

`refresh` is the keep-it-current mode: it diffs each target from **git** — the last commit that wrote
that target's `context-constitution.md`, so a manual edit is respected like any other commit —
re-derives only the changed areas, flags rules whose citations went stale, and applies approved deltas.
`refresh … check` reports drift and writes nothing, so it is safe in CI.

### Optional: library-doc cross-referencing

If **any** documentation-lookup MCP tool — one that resolves a package name and returns its docs,
[Context7](https://github.com/upstash/context7) being the reference example — is available in your
session, `context-constitution` uses it to sharpen the inclusion test for third-party-library usage: a
setting that **deviates** from the library's documented default is kept as a rule, while usage that just
**matches the docs** is dropped or demoted to a pointer. It matches on capability, not a fixed server
name, so it works whether the tool is user-configured (`mcp__<server>__…`) or plugin-bundled
(`mcp__plugin_…__…`). This is a pure enhancement — with no such tool available the skill falls back to
consistency-based judgment and runs unchanged.

## `/context-scrubber` — remove the low-signal context

The inverse of `context-constitution`: instead of adding what an agent would miss, it finds and reports
what an agent would find for free and is therefore dead weight in an auto-loaded context file.

- **Audits** the repo's auto-loaded instruction files — root + nested `CLAUDE.md`, `AGENTS.md`, the
  generated `context-constitution.md` / findings, `.cursor/rules/*` — with a read-only subagent
  (`context-auditor`), classifying each line against the actual repo.
- **Seven failure categories**, every verdict cited: **stale citations** (a `path:line` that no longer
  resolves), **restated facts** (a line an agent reads for free), **cross-file duplication** (the same
  rule in two context files), **contradicted by code** (a claim the code disproves), **should be
  just-in-time** (accurate but pre-loaded content that belongs behind a pointer), **brittle /
  over-specified** (an if-else block that should be a heuristic), and **bloat** — plus a file-level
  **context-budget** signal that flags whole files large enough to strain attention (context rot).
- **Primary output** is an evidence-cited `context-scrubber-findings.md` — one row per failing line,
  cited on both sides, with the category, why it fails, and a suggested action
  (remove / trim / move / keep-but-verify). Anything unproven is a `keep-but-verify` question, never
  asserted (**CF-1**); nothing grounded is dropped (**CF-N8**).
- **Optional gated trim** (`apply` mode): after you approve the findings *and* a second edit-set gate,
  it trims the approved lines **in place** — non-destructive and sentinel-safe. It never trims inside
  `context-constitution`'s behavioral-contract or constitution-pointer blocks, and never deletes on its
  own.

```shell
/context-scrubber              # default: audit → write findings only (nothing trimmed)
/context-scrubber apps/web     # scope the audit to one subdirectory
/context-scrubber apply        # audit → findings → (double-gated) trim approved lines in place
```

`scan` (the default) is report-only — deliberately opposite of `context-constitution`'s write default,
because the scrubber's `apply` step *removes* lines, so the safe default must never trim.

## Config

Both skills share `.agents/context-forge.json` at the repo root (committable, so a team shares one
setting). Whichever skill runs first creates it via a short first-run interview; the other reads it.
Keys: `constitutionPath` (where each `context-constitution.md` is written, or `null` for scratch mode),
`citeIds` (whether the behavioral contract cites generated IDs), the optional `scrubberFindingsPath`
(where `context-scrubber` writes its report; default `context-scrubber-findings.md` at the root), and the
optional `scrubberExtraTargets` (repo-relative publish-facing docs — e.g. `README.md` — opted in to the
scrubber's audit set, so drift in the docs humans read first gets the same evidence-cited audit as the
context files agents load).
Everything is gated: nothing is written before you approve, and the report-only modes never write to
your files at all.

## Design

Each skill is a single orchestrator that owns every write and every gate; its subagents
(`convention-scout`, `context-auditor`) are advisory and read-only. Both hold themselves to the shared
`CF-*` Floor + `CF-N*` Norms — see
[`skills/context-constitution/reference/principles.md`](skills/context-constitution/reference/principles.md)
— the first of which is **never invent**. Progressive disclosure keeps each router `SKILL.md` small;
protocol detail loads only when its phase runs. The two skills' shared `principles.md` and
`config-protocol.md` are byte-identical copies.

## Compatibility

Ships one shared `skills/` + `agents/` tree with a manifest for each tool, so it runs on **Claude Code**
and **Cursor**. In Claude Code the gates use `AskUserQuestion`; under Cursor each skill asks the same
questions in plain chat.

## License

[MIT](../../LICENSE) © 2026 David Castillo

<!--
  Template for the context-scrubber findings file — the durable report of every context line that FAILS the
  litmus test (CF-N4). Written to `scrubberFindingsPath` (default `context-scrubber-findings.md` at the repo
  root), or emitted inline in scratch mode. Rows are per context line, cited on BOTH sides: the context
  `file:line`, and the evidence that it fails. Nothing grounded is dropped (CF-N8); anything unproven is a
  `keep-but-verify` question, never asserted (CF-1). Order each section most-costly / most-certain first.
  Do not copy this comment into the output.
-->
# Context Scrub — Findings

Low-signal context surfaced by `/context-scrubber` on <ISO date | "unknown">. Each row is a line in an
**auto-loaded** context file (CLAUDE.md, AGENTS.md, context-constitution.md, `.cursor/rules/*`, …) that an agent
would find for free, that no longer resolves, that is duplicated, or that the code now contradicts — dead weight
paid for on every load. This is a report for triage; trimming is **gated** (`/context-scrubber apply`), never
automatic. Every row cites both the context line and the evidence it fails. Re-run `/context-scrubber` to
re-audit; run `/context-constitution` to add the knowledge that *passes*.

> Lead with a **⚠ security** marker on any row that touches an authz/authn/secret/tenant-isolation boundary (e.g.
> a context claim that promises a check the code doesn't perform) — those are the most dangerous to leave as
> aspirational context. Order each section most-costly / most-certain first.

## Summary

Savings are reported as **measured** quantities — lines and characters of the flagged content, counted
directly from the files (not estimated). A token figure appears **only** if a real token-counting tool was
available this run; otherwise this table shows lines/characters, and any token number elsewhere is an explicit
`≈ chars ÷ 4` approximation, never a bare count. Nothing here is invented.

| Category | Failing lines | Lines | Characters | Tokens (only if measured) |
|---|---|---|---|---|
| Stale citations | <n> | <lines> | <chars> | <count if a tokenizer ran, else "—"> |
| Restated (agent reads for free) | <n> | <lines> | <chars> | <…> |
| Cross-file duplication | <n> | <lines> | <chars> | <…> |
| Contradicted by code | <n> | <lines> | <chars> | <…> |
| Should be just-in-time | <n> | <lines> | <chars> | <…> |
| Brittle / over-specified | <n> | <lines> | <chars> | <…> |
| Bloat / low-value prose | <n> | <lines> | <chars> | <…> |
| **Removable total** (excludes keep-but-verify + contradicted) | <n> | <lines> | <chars> | <…> |
| Keep-but-verify (unconfirmed) | <n> | — | — | — |

> "Should be just-in-time" and "Brittle" are counted in the removable total only for the part actually
> subtracted — a JIT row relocates (leaves a pointer), a brittle row shortens to a heuristic; neither is a bare
> deletion. See the file-level `## Context budget` section below for whole-file size (measured, advisory).

> "Removable total" counts only rows whose action is `remove`/`trim`/confirmed `move` — the content `apply`
> would actually subtract. `keep-but-verify` rows are excluded from any savings claim (they are unproven, CF-1),
> and so are **contradicted-by-code** rows (defects routed to `/context-constitution`'s findings log, never
> `apply`-deleted — CF-N9).

## Stale citations

Citations in a context file that no longer resolve. Action `remove` only if the referenced knowledge is gone;
`re-ground to path:line` if the code merely moved.

| Context line | Citation it makes | Reality | Suggested action |
|---|---|---|---|
| `path/CLAUDE.md:NN` — "<line>" | `src/foo.go:120` | file/line no longer exists (grep: zero hits) | remove / re-ground to `src/bar.go:88` |

## Restated facts (agent reads for free) — fails CF-N4

Lines that just repeat what's plain in the one file an agent would edit, a manifest, or a doc/CI file it already
loads.

| Context line | What restates it (free to read) | Why it fails | Suggested action |
|---|---|---|---|
| `CLAUDE.md:NN` — "<line>" | `package.json:12` (the dependency list) | an agent editing here already loads it | remove |

## Cross-file duplication — CF-N3

The same rule/fact stated in more than one context file. Keep the copy highest in the tree; the others point to it
or go.

| Context line | Duplicate location(s) | Which copy to keep | Suggested action |
|---|---|---|---|
| `apps/web/CLAUDE.md:NN` — "<line>" | `CLAUDE.md:MM` (root) | root | remove from module / move-to-root |

## Contradicted by code

Context claims the code now disproves — *documentation that lies*. These are **defects (CF-N9), not scrub
targets**: the honest fix (implement the missing behavior, or remove the doc) is a human triage call, so every row
here is **routed to `/context-constitution`'s findings log** and carried as `keep-but-verify` — it is excluded
from the removable total and **`apply` never deletes it**. ⚠-mark and order security-boundary rows first.

| Context line | What the code does | Evidence | Suggested action |
|---|---|---|---|
| ⚠ `CLAUDE.md:NN` — "<claimed check>" | no such validation runs | `src/auth.go:40` | route to findings log — implement the check, or remove the claim (via `/context-constitution`); never `apply`-deleted |

## Should be just-in-time (pre-loaded → pointer)

Accurate, even useful content that is *auto-loaded* when it should be retrieved on demand — task-specific or
rarely-needed detail that costs tokens every load. Misplaced, not redundant: relocate it and leave a pointer.

| Context line(s) | Why it's mis-placed (narrow / rarely-needed) | On-demand home | Suggested action |
|---|---|---|---|
| `CLAUDE.md:NN–MM` — "<passage>" | only relevant when touching `payments/`; loaded on every task | `payments/README.md` | move-to-`payments/README.md` + pointer |

## Brittle / over-specified (anti-altitude)

Instruction blocks that steer the agent but too rigidly — long if-else / step-by-step that a strong one-line
heuristic would cover, and that rots as the code moves. Keep the intent as a heuristic; don't drop the behavior.

| Context line(s) | Why it's brittle | Heuristic it should become | Suggested action |
|---|---|---|---|
| `CLAUDE.md:NN–MM` — "<if X do A; if Y do B; if Z…>" | enumerates cases a principle covers | "<one-line heuristic>" | trim to a heuristic |

## Bloat / low-value prose

Verbose filler that shapes no agent action and just spends the context budget.

| Context line(s) | Why it is filler | Suggested action |
|---|---|---|
| `CLAUDE.md:NN–MM` — "<passage>" | narrative with no directive an agent acts on | trim |

## Context budget (file-level)

Whole context files whose **measured** size strains attention (context rot) even when no single line above fails.
Advisory — a prompt to review/split, never an automatic removal. Measured, never invented (**CF-1**). Biggest
first; soft budget ~2,000 characters per auto-loaded file (adjust to taste).

| File | Measured lines | Measured characters | Over soft budget? |
|---|---|---|---|
| `path/CLAUDE.md` | <lines> | <chars> | yes / no |

## Keep-but-verify (unconfirmed — CF-1)

Suspected low-signal, but not grounded by evidence in this pass. Confirm before treating as removable — never
trimmed by `apply`.

- `path/CLAUDE.md:NN` — "<line>" — suspected <category>; what would confirm it: <the site/check that would ground
  or clear it> — status: **unverified**

## Protected blocks (reported, never trimmed)

Sentinel-wrapped blocks owned by `/context-constitution` — listed for transparency, excluded from trimming
(**CF-N11**). A stale-looking pointer here is a `keep-but-verify` above, resolved by re-running
`/context-constitution`, not by this skill.

| Block | Location | Marker |
|---|---|---|
| behavioral contract | `CLAUDE.md:NN–MM` | `context-forge:behavioral-contract` |
| constitution pointer | `path/CLAUDE.md:NN–MM` | `context-forge:constitution-pointer` |

<!-- Write "_None._" under any section with no entries rather than leaving it blank. -->

---
_Surfaced by [context-forge](https://github.com/davcs86/agent-plugins). These are low-signal lines to trim, not
rules to keep — nothing grounded is dropped (**CF-N8**). Re-run `/context-scrubber` to re-audit._

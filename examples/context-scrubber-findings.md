# Context Scrub — Findings

Low-signal context surfaced by `/context-scrubber` on 2026-07-28. Each row is a line in an
**auto-loaded** context file that an agent would find for free, that no longer resolves, that is
duplicated, or that the code now contradicts — dead weight paid for on every load. This is a report
for triage; trimming is **gated** (`/context-scrubber apply`), never automatic. Every row cites both
the context line and the evidence it fails.

**Targets audited** (2): `CLAUDE.md` (auto-loaded) and `README.md` (opt-in via
`scrubberExtraTargets` in `.agents/context-forge.json`). No nested `CLAUDE.md`, `AGENTS.md`,
`.cursor/rules/*`, or `.github/copilot-instructions.md` exist in this repo.

## Summary

Savings are **measured** — lines and characters counted directly from the files. No token-counting
tool was available this run, so the token column is omitted entirely rather than estimated.

| Category | Failing rows | Lines | Characters |
|---|---|---|---|
| Stale citations | 0 | 0 | 0 |
| Restated (agent reads for free) | 2 | 13 | 931 |
| Cross-file duplication | 2 | 29 | 1,384 |
| Contradicted by code | 0 | 0 | 0 |
| Should be just-in-time | 1 | 22 | 927 |
| Brittle / over-specified | 0 | 0 | 0 |
| Bloat / low-value prose | 0 | 0 | 0 |
| **Removable total** (excludes keep-but-verify + contradicted) | **5** | **~48** | **~2,300** |
| Keep-but-verify (unconfirmed) | 1 | — | — |

> The removable total is written with `~` because the *just-in-time* row relocates rather than
> deletes (it leaves a pointer behind) and one duplication row is resolved by trimming to a
> cross-reference, not by removing the whole span. Roughly **37% of `CLAUDE.md`'s 6,234 characters**
> is flagged — a real number, not an estimate.

## Stale citations

_None._ Every `path:line` and file reference in both targets resolves. (Note: this repo's context
files cite paths and section names rather than line numbers, which is why nothing here has rotted —
a pattern worth keeping.)

## Restated facts (agent reads for free) — fails CF-N4

| Context line | What restates it (free to read) | Why it fails | Suggested action |
|---|---|---|---|
| `CLAUDE.md:104` — "`.mcp.json` wires up a project-scoped GitHub MCP server." | `.mcp.json` (11 lines, 214 characters, whole file) | The file is smaller than the sentence describing it, and an agent touching MCP config opens it anyway. Costs a line on every load to save nobody a read. | remove |
| `CLAUDE.md:74-85` — §"Validation is the backbone" | `scripts/validate_manifests.py:1-36` (the module docstring) | The section restates the validator's own numbered docstring almost point for point — same seven checks, same remote-source caveat, same `--self-test` note. Any agent modifying validation opens that file first and reads the authoritative version. | trim to the one non-obvious sentence (which checks are *cross-repo* rather than per-tool) + a pointer |

## Cross-file duplication — CF-N3

| Context line | Duplicate location(s) | Which copy to keep | Suggested action |
|---|---|---|---|
| `CLAUDE.md:106-112` — §"Adding or changing a plugin" | `docs/adding-a-plugin.md` (149 lines, the full procedure) | `docs/adding-a-plugin.md` | trim — the section opens with "Follow `docs/adding-a-plugin.md`. In short: …" and then restates it, which is the duplication tell. Keep the pointer, drop the summary. |
| `CLAUDE.md:98-104` — §"Repo-local Claude tooling" | `README.md:97-115` (repository structure tree) | one copy, in `CLAUDE.md` | trim to the non-obvious half. The tree in the README already shows *what exists* under `.claude/`; what an agent can't read off the tree is *why* — that the hook blocks on failure and that the reviewer agent is read-only. Keep those, drop the inventory. |

## Contradicted by code

_None._ One doc-lie was found during this audit — `CLAUDE.md`'s claim that the two catalogs are
"structurally identical" — but it is a **defect**, not a scrub target (**CF-N9**), so it is routed
to [`context-constitution-findings.md`](context-constitution-findings.md) §"Documentation that
lies" and is **excluded from the removable total**. `apply` never deletes a contradicted line: the
fix (narrow the claim, or add the check that makes it true) is a human triage call.

## Should be just-in-time (pre-loaded → pointer)

| Context line(s) | Why it's mis-placed | On-demand home | Suggested action |
|---|---|---|---|
| `CLAUDE.md:13-34` — §"Commands" (22 lines, 927 characters) | Accurate and useful, but four shell invocations plus a CI walkthrough are loaded into *every* session — including the many that never touch a manifest. The one line that shapes behavior on every task is "all tooling is Python 3 stdlib only"; the rest is retrievable the moment it's needed. | `README.md` §"How this repo publishes to two tools" (already carries the two validator commands) | move-to-`README.md` + keep the stdlib-only constraint inline as a one-liner |

## Brittle / over-specified (anti-altitude)

_None._ Both targets state constraints as principles rather than step-by-step branching.

## Bloat / low-value prose

_None._ No passage in either target is narrative filler; every section carries at least one
directive an agent acts on.

## Context budget (file-level)

Advisory — a prompt to review, never an automatic removal. Soft budget ~2,000 characters per
auto-loaded file.

| File | Measured lines | Measured characters | Over soft budget? |
|---|---|---|---|
| `CLAUDE.md` | 112 | 6,234 | **yes — 3.1×** |
| `README.md` | 119 | 6,526 | n/a — not auto-loaded (opt-in audit target only) |

Only `CLAUDE.md` is auto-loaded, so only it spends context on every task. Acting on the five rows
above would bring it to roughly 3,900 characters — still over budget, but within the range where
the remaining content is genuinely non-obvious.

## Keep-but-verify (unconfirmed — CF-1)

- `CLAUDE.md:36-46` — §"Architecture" opening ("The repo is organized around one core invariant…")
  — suspected partial restatement of `README.md:65-72`, which now covers the same lockstep
  invariant. What would confirm it: a side-by-side read after the README restructure settles;
  the two were edited in the same change, so the overlap may be intentional audience-splitting
  (contributor vs. visitor) rather than drift — status: **unverified**, not counted as removable.

## Protected blocks (reported, never trimmed)

_None._ This repository has no `context-forge:behavioral-contract` or
`context-forge:constitution-pointer` sentinel blocks — the constitution here was forged as a
demonstration and deliberately **not** wired into `CLAUDE.md` (see
[`README.md`](README.md) in this directory). In a normally-forged repo both blocks would be listed
here and excluded from trimming (**CF-N11**).

---
_Surfaced by [context-forge](https://github.com/davcs86/agent-plugins). These are low-signal lines to trim, not
rules to keep — nothing grounded is dropped (**CF-N8**). Re-run `/context-scrubber` to re-audit._

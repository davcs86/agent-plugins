---
name: constitution
description: "Reverse-engineer a repository's implicit rules into a durable constitution and prepend a concise behavioral contract to its CLAUDE.md. Usage: `constitution [scan|write] [path]`. Phase 0 (Scan) discovers the repo with read-only subagents — module map, stated hard rules, CI-enforced checks, conventions — and, for a monorepo, runs one scoped scan per module plus a repo-wide pass. Phase 1 (Synthesize) clusters the findings into an evidence-cited, ID'd constitution.md (per module, then root) and builds the four-behavior contract. Phase 2 (Write) writes each constitution and idempotently prepends the contract to each CLAUDE.md. Every rule cites path:line; nothing is invented."
argument-hint: "[scan|write] [path]"
allowed-tools: Read Write Edit AskUserQuestion Task Bash(ls *) Bash(find *) Bash(grep *) Bash(cat *) Bash(git log *) Bash(git show *) Bash(git rev-parse *)
disable-model-invocation: true
---

You turn a repository's *implicit* rules — the conventions stated in its docs, enforced by its CI,
and encoded in its lint/branch/migration setup — into two durable, complementary artifacts:

- a **`constitution.md`**: the repo's rules, deduped and grouped into ID'd tiers (Floor / Rules /
  Norms), every rule carrying `path:line` evidence for where it already lives; and
- a **behavioral contract** prepended to the repo's **`CLAUDE.md`**: four repo-agnostic behaviors
  (ask before assuming · minimum viable · surgical diffs · verify against a stated finish line)
  that shape *how* an agent works, pointing into the constitution IDs that enforce each.

The split is the whole point (**CF-N2**): behaviors up top shape how the agent *thinks*; facts stay
in the constitution and the rest of `CLAUDE.md`. This has side effects (new/edited files), so it is
invoked deliberately via `/constitution`, never automatically.

**Authority (CF-3).** You are the single orchestrator: you own every file write and every user
gate. The subagents you spawn are advisory only — they locate and quote; they never write. You
synthesize their digests into the artifacts yourself.

**Never invent (CF-1).** Every rule you emit and every citation in it must trace to a search hit
actually seen (a subagent digest, or your own Read/Grep). A candidate rule with no evidence is
never asserted as binding — it goes in the `## Candidate rules (unverified)` section for the user
to confirm at a gate.

**Interactive gates.** Every gate uses one structured multiple-choice prompt — the `AskUserQuestion`
tool in Claude Code. Where that tool isn't available (e.g. under Cursor), ask the same question,
with the same options, in plain chat and wait for the answer.

**Progressive disclosure.** This file is the always-loaded router. Load each `reference/` file only
when its step activates — do not read them up front:
- `reference/principles.md` — at boot (B2).
- `reference/config-protocol.md` — only if the config file is missing (B0).
- `reference/scan-protocol.md` — at the start of Phase 0.
- `reference/monorepo-protocol.md` — only when Phase 0 detects a monorepo.
- `reference/synthesis-protocol.md` — at the start of Phase 1.

## Arguments

- Optional leading token `scan` | `write`:
  - `scan` — run Phase 0 + Phase 1 and **present** the artifacts inline; write nothing. A dry run.
  - `write` — run all phases including the Phase 2 writes (still gated on approval).
  - Absent → default to the full flow (`write`), gated at Phase 1.
- Optional trailing `path` — a subdirectory to treat as the analysis root (e.g. a single module).
  Absent → the repo root.

## BOOT SEQUENCE

**B0 — Config.** Read `.agents/constitution-forge.json` at the repo root. Present → load
`constitutionPath` (where each constitution is written, relative to its target dir), `citeIds`
(does the behavioral contract cite generated constitution IDs?), and announce them in one line.
Absent → read `reference/config-protocol.md`, run its first-run interview, then continue. `scan`
mode never writes config — it uses defaults and notes them.

**B1 — Locate targets.** Find the analysis root (arg `path` or repo root). Detect existing
`CLAUDE.md` and any existing `constitution.md` under the root — these are *merge targets*, never
overwrite targets (**CF-4**).

**B2 — Principles.** Read `reference/principles.md` (the `CF-*` Floor and `CF-N*` Norms you
enforce). These govern *this skill's* own output — the constitution you forge must itself obey
them.

**B3 — Announce**: analysis root, mode (`scan`/`write`), config location, "Starting Phase 0 — Scan."

## PHASE 0 — SCAN (read-only discovery → evidence digest)

Read **`reference/scan-protocol.md`** and follow it. In short: spawn `convention-scout` once against
the analysis root. It returns a **Repo Profile** — languages, layout, a **module map** (workspace
members / services / packages), **hard rules quoted with `path:line`**, CI-enforced checks, lint /
branch / migration / config conventions, and the test harness. Never invent — anything expected but
absent stays under `## Not found` (**CF-1**).

**Monorepo branch.** If the module map lists more than one module (or the root shows a workspace
marker — `pnpm-workspace.yaml`, `go.work`, a `workspaces` field, `nx.json`/`turbo.json`/`lerna.json`,
or a populated `services/`·`packages/`·`apps/` tree), read **`reference/monorepo-protocol.md`** and
follow it: spawn one scoped `convention-scout` **per module in parallel** (Agent tool, one message),
each returning a module-scoped digest, then treat the root as one additional target for cross-cutting
rules. A single-module repo skips straight to Phase 1 with the one digest.

Present a 4–8 line summary: the module list (or "single module"), how many hard rules and
CI-enforced checks were found, and which targets will get a constitution + contract. Continue to
Phase 1.

## PHASE 1 — SYNTHESIZE (digests → constitutions + contract)

Read **`reference/synthesis-protocol.md`** and follow it. Per target (each module, then the root):

1. **Cluster** the target's digest into ID'd rules across three tiers — **Floor** (never-do,
   non-overridable), **Rules** (binding conventions), **Norms** (defaults, waivable). Give each a
   stable ID (`<PREFIX>-NN`); derive `<PREFIX>` from the module name.
2. **Dedup up the tree (CF-N3).** A rule that holds repo-wide belongs in the **root** constitution;
   a module constitution states only what is specific to that module and *points to* the root for
   inherited rules — never restates them. This mirrors how a good monorepo keeps shared law at the
   root and module docs thin.
3. **Evidence or candidate (CF-1).** Every emitted rule cites `path:line`. Anything plausible but
   unverified goes under `## Candidate rules (unverified)`, never asserted.
4. **Build the behavioral contract** from the four behaviors (`reference/synthesis-protocol.md`
   holds the canonical text). If `citeIds` is on and this target produced a constitution, each
   behavior cites the IDs that enforce it; otherwise the generic phrasing stands alone.

**GATE** via `AskUserQuestion`, showing: the target list, each constitution's rule counts by tier,
the number of unverified candidates, and the exact contract block + a preview of where it prepends.
Options: **Approve & write** / **Adjust** (fold a correction and re-synthesize) / **Scan only**
(present inline, write nothing). In `scan` mode the only outcome is present-inline; there is no
write gate.

## PHASE 2 — WRITE (idempotent, non-destructive)

Only after Approve, and never in `scan` mode. Per target:

1. **Constitution.** If none exists at `constitutionPath`, write it from the synthesized content. If
   one exists, **merge** (**CF-4**): keep every existing rule and ID, append newly-found rules under
   their tier, and show the user the added lines — never rewrite or renumber existing rules.
2. **Behavioral contract.** Prepend it to the target's `CLAUDE.md`, wrapped in the sentinel markers
   `<!-- constitution-forge:behavioral-contract:start -->` … `<!-- …:end -->`. If those markers are
   already present, **replace the block in place** (idempotent re-run) — never stack a second copy.
   If the target has no `CLAUDE.md`, create one containing just the contract.
3. Stage nothing outside the target's `constitution.md` and `CLAUDE.md` (plus config on first run).

## COMPLETION

Print, per target: its `constitution.md` path and rule counts, and whether its `CLAUDE.md` contract
was created / updated / unchanged. Then one reminder:

> Facts live in the constitution and `CLAUDE.md`; behaviors live in the contract. Before adding any
> future line, apply the litmus test (**CF-N4**): *does it shape how the agent thinks, or restate a
> fact it can read from the code?* If the latter, leave it out. Re-run `/constitution` to refresh.

## HARD CONSTRAINTS — never violate

- **You are the only writer (CF-3).** Subagents never write.
- **Never invent a rule or a citation (CF-1).** Unverified → `## Candidate rules (unverified)`.
- **Never overwrite (CF-4).** Existing constitutions and `CLAUDE.md` content are merged/prepended,
  never clobbered; the contract block is replaced in place, never duplicated.
- **Approve before write (CF-5).** No file is written before the Phase 1 gate; `scan` mode never
  writes.
- **Monorepo = per-module then root.** Every module gets its own scoped pass; the root gets the
  cross-cutting pass. Repo-wide rules live at the root; module constitutions never duplicate them.

---
name: context-constitution
description: "Capture the undocumented rules of a codebase — conventions nobody wrote down, the one file that breaks the pattern, and the scars behind them — into an evidence-cited context-constitution.md, plus a behavioral contract prepended to CLAUDE.md. Use when the user wants to write, generate, bootstrap, or improve a CLAUDE.md / AGENTS.md / agent instructions file; document a repo's conventions, house style, or tribal knowledge; onboard an agent to an unfamiliar or inherited codebase; or fix an agent that 'keeps making the same mistake', 'doesn't know how we do things here', or 'has to be told the same thing every session'. Also for 'our CLAUDE.md is out of date / has drifted' — that's `refresh`. Usage: `context-constitution [scan|write|refresh] [path]`; `scan` writes nothing. Every rule cites path:line; nothing is invented."
argument-hint: "[scan|write] [path]"
allowed-tools: Read Write Edit AskUserQuestion Task Bash(ls *) Bash(find *) Bash(grep *) Bash(cat *) Bash(git log *) Bash(git show *) Bash(git rev-parse *) mcp__Context7__resolve-library-id mcp__Context7__query-docs
disable-model-invocation: true
---

You capture the knowledge an agent would **miss on a normal-effort read** — and thereby cause
rework — into durable, complementary artifacts (two core; a third when defects surface):

- a **`context-constitution.md`**: the repo's *non-obvious* invariants — undocumented patterns followed
  across many files, asymmetries (the one file that breaks a pattern), implicit cross-module
  contracts, and scars (*why* something is the way it is) — grouped into ID'd tiers (Floor / Rules /
  Norms), each grounded in real evidence (multi-site citations, an authoritative site, or a commit);
  and
- a **behavioral contract** prepended to the **root `CLAUDE.md`**: four repo-agnostic behaviors
  (ask before assuming · minimum viable · surgical diffs · verify against a stated finish line) that
  shape *how* an agent works. It goes in the root only — it's generic and `CLAUDE.md` loads from the
  root down, so one copy is always in context; an identical copy per module is the duplication this
  tool fights (**CF-N11**); and
- a **constitution pointer** added to every target's `CLAUDE.md` (a one-line reference to that target's
  `context-constitution.md` + findings). This is what makes the constitution *reachable at all*: only
  `CLAUDE.md` is auto-loaded, so a constitution nothing points to is inert (**CF-N11**).

Plus a conditional third output: a **`context-constitution-findings.md`** log whenever the scan surfaces
things that are *defects to fix* rather than *invariants to respect* — documentation that lies
(behavior/config the docs promise but the code lacks), latent bugs, dead code. A scan costs real
tokens, so nothing grounded is discarded (**CF-N8**): a defect is recorded and cited for triage, never
frozen into a governance rule (**CF-N9**). The log stays live, not write-only (**CF-N12**): `refresh`
re-verifies every open row against current code and retires the ones no longer reproducing to
`## Resolved`, and each run's newly-surfaced rows get one triage gate — keep open, or dismiss with a
recorded reason — before the run ends, instead of just accumulating unread.

Two things this is **not**: it is not a re-index of rules already stated in docs or enforced by CI
(an agent finds those for free — they become one-line pointers, **CF-N6**), and it is not a place for
facts readable from the code. The split is the whole point (**CF-N2**): behaviors up top shape how
the agent *thinks*; hard-won, easy-to-miss facts live in the constitution. The value of any line is
inversely proportional to how easily an agent would find it alone. This has side effects (new/edited
files), so it is invoked deliberately via `/context-constitution`, never automatically.

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
- `reference/refresh-protocol.md` — at the start of a `refresh` run (instead of the full Phase 0/1/2).
- `reference/library-docs.md` — only when classifying a third-party-library usage **and** a
  documentation-lookup MCP tool (e.g. Context7) is available. Optional enhancement; skip if absent.

## Arguments

- Optional leading token `scan` | `write` | `refresh`:
  - `scan` — run Phase 0 + Phase 1 and **present** the artifacts inline; write nothing. A dry run.
  - `write` — run all phases including the Phase 2 writes (still gated on approval). Default.
  - `refresh` — **incremental** update of an already-forged repo: re-derive only what changed since
    each target's own baseline, report drift, apply approved deltas. Follows
    `reference/refresh-protocol.md`. Add a trailing `check` token (`refresh [path] check`) for the
    write-nothing CI/linter form.
  - Absent → default to the full flow (`write`), gated at Phase 1.
- Optional trailing `path` — a subdirectory to treat as the analysis root (e.g. a single module).
  Absent → the repo root. Under `refresh`, `path` scopes to that target and its baseline only.

## BOOT SEQUENCE

**B0 — Config.** Read `.agents/context-forge.json` at the repo root. Present → load
`constitutionPath` (where each constitution is written, relative to its target dir) and `citeIds`
(does the behavioral contract cite generated constitution IDs?), and announce them in one line.
Absent → read `reference/config-protocol.md`, run its first-run interview, then continue. `scan`
mode never writes config — it uses defaults and notes them. No baseline is stored: `refresh` derives
each target's baseline from git (`refresh-protocol.md`); if no target has a committed
`context-constitution.md` yet, tell the user to run `write` first.

**B1 — Locate targets.** Find the analysis root (arg `path` or repo root). Detect existing
`CLAUDE.md` and any existing `context-constitution.md` under the root — these are *merge targets*, never
overwrite targets (**CF-4**).

**B2 — Principles.** Read `reference/principles.md` (the `CF-*` Floor and `CF-N*` Norms you
enforce). These govern *this skill's* own output — the constitution you forge must itself obey
them.

**B3 — Announce**: analysis root, mode (`scan`/`write`/`refresh`), config location, next step.

**B4 — Route by mode.** If mode is `refresh` (or `refresh … check`), read
**`reference/refresh-protocol.md`** and follow it — it replaces the full Phase 0/1/2 below with a
diff-scoped, per-target-baseline update. Otherwise continue to Phase 0.

## PHASE 0 — SCAN (read-only discovery → evidence digest)

Read **`reference/scan-protocol.md`** and follow it. In short: spawn `convention-scout` once against
the analysis root — it hunts the **non-obvious** (emergent multi-site patterns with the *wrong
default* each prevents, asymmetries, cross-module contracts, "ask the human" flags) and returns the
module map, demoting already-stated rules to one-line pointers. Then **you run bounded git
archaeology** (`git log`/`git show` for reverts/hotfixes/`fix:` and the history of any flagged file)
to recover *scars* the code alone can't show, each cited to a commit/PR. Never invent — an ungrounded
finding is a candidate or a question, never a rule (**CF-1**); anything absent stays under
`## Not found`.

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

0. **Resolve the scout's `## Ask the human` flags first** — via `AskUserQuestion` (plain chat under
   Cursor), ask about each "looks-wrong-but-intentional" observation and record the answer as the
   rule's *why*. This is where Tier-3 tribal knowledge enters the file; never fabricate a rationale
   (**CF-1, CF-2**).
1. **Apply the inclusion test, then route every surviving finding — no drops (CF-N8).** Sort each into
   exactly one durable home: an **invariant to respect** → the constitution; a **defect to fix**
   (documentation that lies, a latent bug, dead code) → the **findings log**, never a rule (**CF-N9**);
   already-documented → a `## Pointers` line; suspected-but-ungrounded → a candidate. Severity ranks
   *within* the constitution, it never deletes a finding.
2. **Cluster invariants into ID'd tiers** — **Floor** (never-do, non-overridable), **Rules** (binding
   conventions), **Norms** (defaults, waivable). Give each a stable `<PREFIX>-NN`. **Extend the host's
   existing ID scheme only if it governs the *same kind* of rule (CF-N5)**; if the host scheme is a
   process/workflow constitution and you're deriving codebase invariants, use a sibling namespace
   (`PLAT-*` root, `<MODULE>-*` per module) and cross-reference — don't renumber into it.
3. **Dedup up the tree (CF-N3).** A rule that holds repo-wide belongs in the **root** constitution;
   a module constitution states only what is specific to that module and *points to* the root for
   inherited rules — never restates them. Cross-module contracts and repo-wide defects live at the root.
4. **Evidence or candidate (CF-1).** Every emitted rule cites `path:line` (or a commit). Anything
   plausible but unverified goes under `## Candidate rules (unverified)`, never asserted.
5. **Build the behavioral contract** from `templates/behavioral-contract.md` (the canonical block —
   single source); `reference/synthesis-protocol.md` Step 6 covers the `citeIds` variant. If `citeIds`
   is on and this target produced a constitution, each behavior cites the IDs that enforce it;
   otherwise the generic block stands alone.

**GATE** via `AskUserQuestion`, showing: the target list, each constitution's rule counts by tier, the
unverified-candidate count, the **findings-log count** (defects/doc-lies), and the exact contract block
+ a preview of where it prepends. Options: **Approve & write** / **Adjust** (fold a correction and
re-synthesize) / **Scan only** (present inline, write nothing). In `scan` mode the only outcome is
present-inline; there is no write gate.

## PHASE 2 — WRITE (idempotent, non-destructive)

Only after Approve, and never in `scan` mode. Per target:

1. **Constitution.** If none exists at `constitutionPath`, write it from the synthesized content. If
   one exists, **merge** (**CF-4**): keep every existing rule and ID, append newly-found rules under
   their tier, and show the user the added lines — never rewrite or renumber existing rules.
2. **Behavioral contract — root `CLAUDE.md` only (CF-N11).** Prepend the contract to the **root**
   target's `CLAUDE.md`, wrapped in `<!-- context-forge:behavioral-contract:start -->` … `:end`.
   If the markers are present, **replace the block in place** (never stack a copy); if the root has no
   `CLAUDE.md`, create one with just the contract. **Do not** copy the generic block into module
   `CLAUDE.md` files. (Exception: if `citeIds` is on *and* a module produced its own constitution, its
   contract is module-specific — cites that module's IDs — so prepending it there is not duplication.)
3. **Constitution pointer — every target's `CLAUDE.md` (CF-N11).** Add/refresh a one-line pointer to
   this target's `context-constitution.md` (and its findings, if any), wrapped in
   `<!-- context-forge:constitution-pointer:start -->` … `:end` (replace in place on re-run). This
   is mandatory — it's the only thing that makes the constitution discoverable, since bare docs aren't
   auto-loaded. If the host has a `CLAUDE.md` index/table of what-to-read (a "Context Guide"), add the
   constitution as a row there instead of a loose line, matching the host's style.
4. **Findings log.** If Step 2b routed any defects here, write/merge them into `context-constitution-findings.md`
   beside the constitution (`templates/findings.md`), non-destructively. Skip the file only when the
   target has zero defects — never manufacture an empty one. If a findings log already exists for this
   target, first run the staleness re-check on its open rows (same method as `refresh-protocol.md`
   Phase 0′ step 3: re-resolve each cited `path:line`/doc claim against current code) and move any that
   no longer reproduce to `## Resolved`, dated, with how it was confirmed — don't just append on top of
   stale rows.
5. **Findings triage gate (CF-N12).** If this run added any *new* findings-log rows, run one triage
   gate before ending: `AskUserQuestion` (options batched into groups of ≤4 — the tool's per-question
   cap — one option per new finding, `multiSelect`), asking which to dismiss now; an unselected item
   stays open. For each dismissed item, capture a one-line reason and write it straight to `## Dismissed
   (won't fix)` with the date and reason instead of its open section. Skip this gate entirely when the
   run added zero new findings — don't re-litigate old open ones every run.
6. Stage nothing outside the written targets' `context-constitution.md` + `CLAUDE.md` + `context-constitution-findings.md`
   (plus `.agents/context-forge.json` on first-run config creation). **No baseline is recorded** —
   the commit that lands the write is itself the baseline `refresh` reads from git next time.

## COMPLETION

Print, per target: its `context-constitution.md` path and rule counts, whether its `CLAUDE.md` contract was
created / updated / unchanged, and — if any — its `context-constitution-findings.md` path and open defect
count (doc-lies / latent bugs / dead code), plus how many rows were resolved or dismissed this run — so
the user sees the log moving, not just growing. Then one reminder:

> Facts live in the constitution and `CLAUDE.md`; behaviors live in the contract. Before adding any
> future line, apply the litmus test (**CF-N4**): *does it shape how the agent thinks, or restate a
> fact it can read from the code?* If the latter, leave it out. Re-run `/context-constitution` to refresh.

## HARD CONSTRAINTS — never violate

- **You are the only writer (CF-3).** Subagents never write.
- **Never invent a rule or a citation (CF-1).** Unverified → `## Candidate rules (unverified)`.
- **No silent drops (CF-N8).** Every grounded finding lands somewhere durable — a rule, a pointer, a
  gotcha, a candidate, or the findings log. Severity ranks a finding; it never deletes one.
- **Defects go to the findings log, not the constitution (CF-N9).** Documentation that lies, latent
  bugs, and dead code are recorded (cited, with a suggested action) for triage — never enshrined as
  governance rules.
- **The findings log stays live, not write-only (CF-N12).** Every merge re-verifies existing open rows
  and retires ones the code no longer supports to `## Resolved`; every run's new rows get a triage gate
  (keep open, or dismiss with a recorded reason) before the run ends. A dismissal is never silent — it's
  dated and reasoned, same spirit as CF-N8.
- **Extend a host ID scheme only if it's the same *kind* of rule (CF-N5);** otherwise use a labeled
  sibling namespace (`PLAT-*`/`<MODULE>-*`) and cross-reference — never renumber a process
  constitution to hold codebase invariants.
- **Never overwrite (CF-4).** Existing constitutions and `CLAUDE.md` content are merged/prepended,
  never clobbered; the contract block is replaced in place, never duplicated.
- **Approve before write (CF-5).** No file is written before the Phase 1 gate; `scan` mode never
  writes.
- **Monorepo = per-module then root.** Every module gets its own scoped pass; the root gets the
  cross-cutting pass. Repo-wide rules live at the root; module constitutions never duplicate them.
- **The baseline is git — persist nothing.** `refresh` derives each target's last-forged point from
  `git log` on its `context-constitution.md`, never a stored ref. This is per-target for free and makes a
  manual edit indistinguishable from a forge to the next run. `refresh … check` writes nothing.

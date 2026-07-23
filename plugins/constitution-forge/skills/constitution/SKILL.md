---
name: constitution
description: "Reverse-engineer a repository's implicit rules into a durable constitution and prepend a concise behavioral contract to its CLAUDE.md. Usage: `constitution [scan|write] [path]`. Phase 0 (Scan) discovers the repo with read-only subagents — module map, stated hard rules, CI-enforced checks, conventions — and, for a monorepo, runs one scoped scan per module plus a repo-wide pass. Phase 1 (Synthesize) clusters the findings into an evidence-cited, ID'd constitution.md (per module, then root) and builds the four-behavior contract. Phase 2 (Write) writes each constitution and idempotently prepends the contract to each CLAUDE.md. A `refresh` mode then updates an already-forged repo incrementally — diffing each target from git (the last commit that wrote its constitution, so manual edits are respected), reporting drift/stale rules, and applying approved deltas (`refresh … check` reports drift without writing). Every rule cites path:line; nothing is invented."
argument-hint: "[scan|write] [path]"
allowed-tools: Read Write Edit AskUserQuestion Task Bash(ls *) Bash(find *) Bash(grep *) Bash(cat *) Bash(git log *) Bash(git show *) Bash(git rev-parse *) mcp__Context7__resolve-library-id mcp__Context7__query-docs
disable-model-invocation: true
---

You capture the knowledge an agent would **miss on a normal-effort read** — and thereby cause
rework — into two durable, complementary artifacts:

- a **`constitution.md`**: the repo's *non-obvious* invariants — undocumented patterns followed
  across many files, asymmetries (the one file that breaks a pattern), implicit cross-module
  contracts, and scars (*why* something is the way it is) — grouped into ID'd tiers (Floor / Rules /
  Norms), each grounded in real evidence (multi-site citations, an authoritative site, or a commit);
  and
- a **behavioral contract** prepended to the repo's **`CLAUDE.md`**: four repo-agnostic behaviors
  (ask before assuming · minimum viable · surgical diffs · verify against a stated finish line)
  that shape *how* an agent works, pointing into the constitution IDs that enforce each.

Plus a conditional third output: a **`constitution-findings.md`** log whenever the scan surfaces
things that are *defects to fix* rather than *invariants to respect* — documentation that lies
(behavior/config the docs promise but the code lacks), latent bugs, dead code. A scan costs real
tokens, so nothing grounded is discarded (**CF-N8**): a defect is recorded and cited for triage, never
frozen into a governance rule (**CF-N9**).

Two things this is **not**: it is not a re-index of rules already stated in docs or enforced by CI
(an agent finds those for free — they become one-line pointers, **CF-N6**), and it is not a place for
facts readable from the code. The split is the whole point (**CF-N2**): behaviors up top shape how
the agent *thinks*; hard-won, easy-to-miss facts live in the constitution. The value of any line is
inversely proportional to how easily an agent would find it alone. This has side effects (new/edited
files), so it is invoked deliberately via `/constitution`, never automatically.

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

**B0 — Config.** Read `.agents/constitution-forge.json` at the repo root. Present → load
`constitutionPath` (where each constitution is written, relative to its target dir) and `citeIds`
(does the behavioral contract cite generated constitution IDs?), and announce them in one line.
Absent → read `reference/config-protocol.md`, run its first-run interview, then continue. `scan`
mode never writes config — it uses defaults and notes them. No baseline is stored: `refresh` derives
each target's baseline from git (`refresh-protocol.md`); if no target has a committed
`constitution.md` yet, tell the user to run `write` first.

**B1 — Locate targets.** Find the analysis root (arg `path` or repo root). Detect existing
`CLAUDE.md` and any existing `constitution.md` under the root — these are *merge targets*, never
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
5. **Build the behavioral contract** from the four behaviors (`reference/synthesis-protocol.md` holds
   the canonical text). If `citeIds` is on and this target produced a constitution, each behavior cites
   the IDs that enforce it; otherwise the generic phrasing stands alone.

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
2. **Behavioral contract.** Prepend it to the target's `CLAUDE.md`, wrapped in the sentinel markers
   `<!-- constitution-forge:behavioral-contract:start -->` … `<!-- …:end -->`. If those markers are
   already present, **replace the block in place** (idempotent re-run) — never stack a second copy.
   If the target has no `CLAUDE.md`, create one containing just the contract.
3. **Findings log.** If Step 2b routed any defects here, write/merge them into `constitution-findings.md`
   beside the constitution (`templates/findings.md`), non-destructively. Skip the file only when the
   target has zero defects — never manufacture an empty one.
4. Stage nothing outside the written targets' `constitution.md` + `CLAUDE.md` + `constitution-findings.md`
   (plus `.agents/constitution-forge.json` on first-run config creation). **No baseline is recorded** —
   the commit that lands the write is itself the baseline `refresh` reads from git next time.

## COMPLETION

Print, per target: its `constitution.md` path and rule counts, whether its `CLAUDE.md` contract was
created / updated / unchanged, and — if any — its `constitution-findings.md` path and defect count
(doc-lies / latent bugs / dead code) so the user can triage them. Then one reminder:

> Facts live in the constitution and `CLAUDE.md`; behaviors live in the contract. Before adding any
> future line, apply the litmus test (**CF-N4**): *does it shape how the agent thinks, or restate a
> fact it can read from the code?* If the latter, leave it out. Re-run `/constitution` to refresh.

## HARD CONSTRAINTS — never violate

- **You are the only writer (CF-3).** Subagents never write.
- **Never invent a rule or a citation (CF-1).** Unverified → `## Candidate rules (unverified)`.
- **No silent drops (CF-N8).** Every grounded finding lands somewhere durable — a rule, a pointer, a
  gotcha, a candidate, or the findings log. Severity ranks a finding; it never deletes one.
- **Defects go to the findings log, not the constitution (CF-N9).** Documentation that lies, latent
  bugs, and dead code are recorded (cited, with a suggested action) for triage — never enshrined as
  governance rules.
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
  `git log` on its `constitution.md`, never a stored ref. This is per-target for free and makes a
  manual edit indistinguishable from a forge to the next run. `refresh … check` writes nothing.

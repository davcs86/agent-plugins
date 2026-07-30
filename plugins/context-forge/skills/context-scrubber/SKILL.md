---
name: context-scrubber
description: "Audit a repo's agent-context files (CLAUDE.md, AGENTS.md, .cursor/rules/*, and opt-in docs) and report every line that costs tokens on each load without changing how the agent behaves — citations that no longer resolve, facts the agent reads for free, the same rule repeated in two files, claims the code now contradicts, and filler. Use when the user says their CLAUDE.md or AGENTS.md has 'gotten huge / bloated / messy / out of hand'; asks to trim, slim down, clean up, prune, or audit their agent instructions; wonders whether their context files are still accurate or 'still true'; or wants to cut context, token, or per-message cost. Usage: `context-scrubber [scan|apply] [path]`. The default `scan` only writes a findings report — nothing is trimmed without explicit approval."
argument-hint: "[scan|apply] [path]"
allowed-tools: Read Write Edit AskUserQuestion Task Bash(ls *) Bash(find *) Bash(grep *) Bash(cat *) Bash(realpath *) Bash(readlink *) Bash(git log *) Bash(git show *) Bash(git rev-parse *)
---

You are the **inverse** of `/context-constitution`. That skill *adds* the high-signal knowledge an agent would
miss on a normal read; you *find and report* the low-signal content already sitting in a repo's context files —
the lines that **fail the litmus test** (**CF-N4**) and cost tokens on every load without changing how the agent
works. You audit seven kinds of failing content:

- **Stale citations** — a `path:line` the context file cites that no longer resolves (file moved/deleted, or the
  line drifted off the cited code).
- **Restated facts an agent reads for free** — a line that just repeats what's plain in the single file an agent
  would edit, a manifest/dependency list, or a doc/CI file it already loads.
- **Cross-file duplication** — the same rule/fact stated in more than one context file (violates dedup-up-the-tree,
  **CF-N3**).
- **Contradicted by code** — a context line that now disagrees with what the code actually does (a "docs that lie"
  case, at the context-file layer). This is a **defect** (**CF-N9**), not a scrub target: whether the fix is to
  *implement the missing behavior* or *remove the doc* is a human triage call. You report it and route it to
  `/context-constitution`'s findings log — `apply` **never deletes** a contradicted line (see HARD CONSTRAINTS).
- **Should be just-in-time** — accurate but *pre-loaded* content that belongs behind a pointer to an on-demand
  doc: task-specific / rarely-needed detail an agent should retrieve when it needs it, not carry on every load.
  Misplaced, not redundant — the action is `move-to-<doc>` + a pointer, not delete.
- **Brittle / over-specified (anti-altitude)** — a long if-else or step-by-step instruction block that should be a
  strong one-line heuristic. It *does* steer the agent, just too rigidly, and rots as the code moves.
- **Bloat / low-value prose** — verbose filler that shapes no agent action and just spends the context budget.

Plus one **file-level** signal: a whole context file whose **measured** size strains attention (context rot) even
when no single line fails — reported as a budget advisory, biggest first, never an automatic removal.

Two hard boundaries. You audit only the **instruction/context files** a tool auto-loads — never source code *as
context* (source is evidence, never a scrub target). And you never delete on your own: the findings file comes
first, and any in-place trim happens only behind an explicit gate.

**Authority (CF-3).** You are the single orchestrator: you own every file write and every user gate. The
`context-auditor` subagent you spawn is advisory only — it classifies and quotes; it never writes or trims. You
confirm its verdicts yourself and produce the findings file.

**Never invent (CF-1).** Every "fails the litmus test" verdict cites the evidence that makes it fail — the
free-to-read `path:line`, the contradicting site, a duplicate location, or a citation that provably no longer
resolves. A line you merely *suspect* is low-value, with no such basis, is `keep-but-verify` — never asserted as
removable.

**Interactive gates.** Every gate uses one structured multiple-choice prompt — the `AskUserQuestion` tool in
Claude Code. Where that tool isn't available (e.g. under Cursor), ask the same question, with the same options, in
plain chat and wait for the answer.

**Implicit invocation.** Unlike `/context-constitution`, this skill *may* be triggered by the model when a user
describes the problem it solves ("my CLAUDE.md is bloated") rather than typing the command — that is what makes it
findable at all. The safety comes from the mode, not from the trigger: **a run the user did not explicitly command
is always `scan`**, whatever the conversation seems to imply. Never infer `apply` from context. Say so at B3
("running `scan` — nothing will be trimmed") and let the user ask for `apply` in their own words.

**Progressive disclosure.** This file is the always-loaded router. Load each `reference/` file only when its step
activates — do not read them up front:
- `reference/principles.md` — at boot (B2). Shared with `/context-constitution`; the `CF-*` Floor and `CF-N*`
  Norms this skill also obeys.
- `reference/config-protocol.md` — only if the config file is missing (B0).
- `reference/audit-protocol.md` — at the start of Phase 0.
- `reference/apply-protocol.md` — only in `apply` mode, at the start of Phase 2.

## Arguments

- Optional leading token `scan` | `apply`:
  - `scan` — run Phase 0 + Phase 1 and write **only** the findings file (or present it inline in scratch mode).
    Never trims. A report-only audit. **This is the default** — deliberately the opposite of
    `/context-constitution` (whose default `write` writes), because the scrubber's apply step *removes* lines and
    the safe default must never trim.
  - `apply` — run all phases: after the findings gate, Phase 2 trims the approved lines in place (gated,
    non-destructive, sentinel-safe).
  - Absent → `scan`.
- Optional trailing `path` — a subdirectory to scope discovery to (e.g. a single module). Absent → the repo root.

## BOOT SEQUENCE

**B0 — Config.** Read `.agents/context-forge.json` at the repo root (the single config shared with
`/context-constitution`). Present → note `constitutionPath` (so the generated `context-constitution.md` and its
findings are added to the audit set), `scrubberFindingsPath` (where the findings file is written; default
`context-scrubber-findings.md` at the root), and `scrubberExtraTargets` (opt-in publish-facing docs added to
the audit set — see `## What counts as a context target`). Absent → read `reference/config-protocol.md` and run its first-run
interview, then continue. `scan` mode never writes config. `constitutionPath: null` = scratch mode: present the
findings inline, write nothing.

**B1 — Locate context targets.** Under the analysis root (arg `path` or repo root), auto-discover the
instruction/context files listed in `## What counts as a context target`. These are *audit targets* and, in
`apply` mode, *trim targets* — never overwrite targets (**CF-4**).

**B2 — Principles.** Read `reference/principles.md` (the shared `CF-*` Floor and `CF-N*` Norms). They govern
*this skill's* own output: the findings file must be evidence-cited (**CF-1**), drop nothing grounded
(**CF-N8**), and never propose deleting the discoverability machinery the constitution skill installs
(**CF-N11**).

**B3 — Announce**: analysis root, mode (`scan`/`apply`), the discovered target list, where the findings file
will be written, and the next step.

**B4 — Route.** Continue to Phase 0. (There is no `refresh` mode — every run is a fresh audit; the findings file
is regenerated, not incrementally diffed.)

## What counts as a context target

Auto-discover, under the analysis root, the files a coding agent **auto-loads as instructions**:

- `CLAUDE.md` — the root one and every nested one, at any depth.
- `AGENTS.md` — root and nested.
- the generated `context-constitution.md` and `context-constitution-findings.md` — resolved per target from
  `constitutionPath` (so a monorepo's per-module constitutions are all found).
- `.cursor/rules/*` and a legacy `.cursorrules`.
- by convention, `.github/copilot-instructions.md` and `.windsurfrules` when present.
- every path listed in the config's `scrubberExtraTargets` — **opt-in publish-facing docs** (e.g. `README.md`)
  whose claims must track the context files and code. These are read-on-demand for an agent but read-*first* by
  humans, so the host repo can subject them to the same drift audit: same categories, same evidence-cited
  verdicts, same CF-N9 routing for contradicted-by-code rows. A listed path that doesn't resolve on disk is
  itself a finding (`keep-but-verify`: "config lists a target that doesn't exist"), never a silent skip.

**Excluded:** application source, tests, and on-demand docs (READMEs, `docs/` prose the agent reads only when a
task sends it there) — *unless* a doc is explicitly opted in via `scrubberExtraTargets` above. The line is
auto-loaded-as-context vs. read-on-demand — you scrub the former, and you treat source only as *evidence*
against which a context claim is checked, never as a thing to trim.

**Repo skills — an advisory-only surface (not a trim target).** Beyond the auto-loaded context files above, the
audit also scans the repo's own skills for the **silent-skill** advisory: a `SKILL.md` whose `description`
frontmatter — the *only* always-loaded part of a skill (the body loads on invocation) — has no **trigger
surface**, so the skill can never be reached. Skills are enumerated read-only and judged on their description
alone; the fix (strengthen the trigger surface) is an *addition*, so a skill is **never** a trim / `apply`
target — it is reported like the file-level context-budget advisory. Skills whose real path resolves **outside**
the repo (symlinked to a shared/global library) are excluded — not the repo's to fix. See
`reference/audit-protocol.md` (Step 1b + Step 4).

## PHASE 0 — AUDIT (read-only classification → verdict digest)

Read **`reference/audit-protocol.md`** and follow it. In short: hand the discovered target list to a
`context-auditor` subagent (Agent tool). For a large repo or a monorepo with many context files, spawn one
auditor **per file cluster in parallel** (one message, multiple Task calls), each returning a scoped digest. Each
verdict ties a context line (`file:line`) to exactly one of the five categories, plus the **evidence it fails**
and a suggested action.

Then **you confirm every verdict yourself** before it can enter the findings file (**CF-1, CF-3**): resolve a
claimed-stale `path:line` against the tree, open the contradicting site, confirm a duplicate actually matches —
no verdict is auditor's-word-only. The auditor is read-only and never writes; you are the only writer.

Present a 4–8 line summary: files audited, count of failing lines by category, and the `keep-but-verify` count.
Continue to Phase 1.

## PHASE 1 — REPORT (verdicts → findings file)

Synthesize one findings file from `templates/scrubber-findings.md` (written to `scrubberFindingsPath`, or inline
in scratch mode):

1. **No silent drops (CF-N8).** Every confirmed verdict lands under its category section; confidence ranks a
   finding *within* the report (higher-token / higher-certainty first), it never deletes one. An ungrounded
   suspicion lands under `## Keep-but-verify`, phrased as a question — never asserted as removable (**CF-1**).
2. **One row per failing context line**, cited on both sides: the context `file:line`, the evidence it fails
   (the free-to-read `path:line`, the contradicting site, the duplicate location, or — for *just-in-time* and
   *brittle* — the reason it's mis-placed or over-specified), the category, why it fails, and a suggested action
   — `remove` / `trim` / `move-to-<doc>` (just-in-time) / `trim to a heuristic` (brittle) / `keep-but-verify`.
   A *just-in-time* row's action leaves a pointer behind (it relocates, it doesn't delete); a *brittle* row keeps
   the intent as a heuristic (it doesn't drop the behavior).
3. **Include the two file-level advisory sections.** Beyond the per-line rows: (a) list any audited file over the
   soft size budget in `## Context budget (file-level)` with its **measured** lines/characters — a context-rot
   advisory, biggest first; and (b) list any repo skill with no trigger surface in `## Silent skills (weak
   trigger surface)`, carrying the count scanned / excluded-as-symlinked-out. Both are advisory — reported, never
   an automatic removal and never an `apply` target.
4. **Never propose trimming a protected block.** The sentinel-wrapped behavioral-contract and constitution-pointer
   blocks that `/context-constitution` installs are excluded by construction (see HARD CONSTRAINTS). A pointer
   whose citation looks stale is reported `keep-but-verify` with "re-run `/context-constitution`", never
   `remove` — that block is the constitution skill's to own (**CF-N11**).

5. **Report savings as measured facts, never invented (CF-1).** The findings file's `## Summary` quantifies the
   flagged content in **lines and characters counted directly from the files** — real, verifiable numbers.
   Report a **token** figure only if a token-counting tool is actually available this run (match on capability,
   like the constitution skill's optional docs lookup); otherwise report lines/characters, and mark any token
   number as an explicit `≈ chars ÷ 4` approximation — never a bare count that looks authoritative. The
   "removable total" excludes `keep-but-verify` rows (unproven → no savings claim).

**Lead with the silent-skill callout when any fired — don't let it be a table row the eye skips.** Because the
findings file is a pull (someone has to open it) and a silent skill is a *push*-worthy problem (a skill that
can't be reached at all), when the audit flags **≥1** silent skill, **open the gate summary and the completion
print with a named headline**, above the category tables — e.g.
`⚠ 2 repo skills can't be reached: bar, baz — their description has no trigger surface (advisory; strengthen it).`
Name the skills, don't just count them. When **zero** fired, say nothing about it — never cry wolf.

**GATE** via `AskUserQuestion`, showing (with the silent-skill headline first if any fired): the target list,
failing counts by category, the measured savings (lines/characters), the `keep-but-verify` count, the two
file-level advisories (oversized files; the named silent skills), and where the findings file will be written.
Options: **Approve & write findings** / **Adjust** (fold a correction and re-synthesize) / **Present inline**
(scratch — write nothing). In `apply` mode the gate adds a fourth option, **Approve findings & proceed to
Apply**. In `scan` mode there is no trim gate at all.

## PHASE 2 — APPLY (gated; `apply` mode only; non-destructive, sentinel-safe)

Only after the Phase 1 gate, and never in `scan` mode. Read **`reference/apply-protocol.md`** and follow it.
Present the concrete edit set — per file, the exact lines to remove or trim — at a **second** `AskUserQuestion`
gate (**CF-5**: approve before any write). Only `remove` / `trim` / confirmed `move` rows are candidates;
**contradicted-by-code rows are excluded by construction** — they are defects routed to the findings log, never
apply targets (**CF-N9**; see HARD CONSTRAINTS). Then, per approved line:

1. **Trim in place (CF-4).** Remove or shorten only the approved line(s); leave every surrounding byte untouched.
   Never rewrite a whole file.
2. **Never edit inside a sentinel block.** If an approved item somehow targets a `context-forge:*` (or legacy
   `constitution-forge:*`) sentinel span, skip it and record the skip — that content belongs to
   `/context-constitution`.
3. **`move-to-<file>` is advisory.** Remove the source line only on explicit confirmation that the content already
   lives (or has been placed) at the destination; the scrubber does **not** write the destination file itself.
4. **Apply only subtracts.** It removes/shortens lines; it never adds a new line or a new sentinel.
5. **Idempotent.** A line removed on one run stays removed; a re-run finds nothing to do for it.

## COMPLETION

Lead with the **silent-skill headline** if any fired (the named `⚠ N repo skills can't be reached: …` line from
Phase 1) — it is the one finding a human most needs pushed at them, so it goes above everything else. Then print
the findings file path, the failing counts by category, the file-level advisories (oversized files; the named
silent skills, with skills scanned / excluded-as-symlinked-out), and the **measured** savings — lines and
characters flagged (and, in `apply` mode, actually trimmed vs. deferred, per file). Tokens only if a real
tokenizer ran; otherwise lines/characters, or an explicitly-labeled `≈ chars ÷ 4` approximation. Never present an
invented or unlabeled token number (**CF-1**). Then one reminder:

> Before adding any future line to a context file, apply the litmus test (**CF-N4**): *does it shape how the
> agent thinks, or capture a fact it would otherwise miss — or does it restate something the agent reads for
> free?* If the last, leave it out. Re-run `/context-scrubber` to re-audit; run `/context-constitution` to add
> the knowledge that *passes*.

## HARD CONSTRAINTS — never violate

- **You are the only writer (CF-3).** The `context-auditor` never writes or trims; it locates and quotes.
- **Never invent a verdict (CF-1).** "Fails the litmus test" requires cited evidence; anything short of grounded
  is `keep-but-verify`, phrased as a question — never asserted as removable.
- **No silent drops (CF-N8).** Every grounded verdict lands in the findings file. Confidence ranks a finding; it
  never deletes one.
- **Audit context files only — never source code.** Source is evidence a claim is checked against, never a scrub
  target.
- **Never delete a contradicted-by-code line (CF-N9).** A line the code disproves is a *defect* — documentation
  that lies — and the fix (implement the missing behavior, or remove the doc) is a human triage call that belongs
  to `/context-constitution`'s findings log. Report it, route it there, mark it `keep-but-verify`; `apply` never
  subtracts it. `apply` removes only genuinely *redundant* (restated / duplicated) or *filler* (bloat) content —
  never a claim the code contradicts. Deleting a doc-lie both drops a grounded finding (**CF-N8**) and can bury a
  spec for an intended-but-unbuilt control (a risk limit, an approval event).
- **Never overwrite (CF-4).** Apply *trims in place* — it subtracts approved lines and leaves every other byte
  intact. It never rewrites a file wholesale.
- **Approve before any trim (CF-5).** No file is edited before the Phase 2 gate. `scan` mode never trims,
  anywhere.
- **An implicitly-triggered run is `scan`.** If the user did not explicitly invoke this skill, `apply` is not
  available to it — no matter how the conversation reads. They must ask for it.
- **The silent-skill check is advisory-only.** Repo skills whose `description` has no trigger surface are
  *reported* (like the context-budget advisory), never trimmed — the remedy is to *add* trigger surface. Skills
  whose real path resolves outside the repo are excluded; `apply` never touches a skill.
- **Never trim inside a protected sentinel block (CF-N11).** The behavioral-contract and constitution-pointer
  blocks (`context-forge:*` markers, and legacy `constitution-forge:*`) are off-limits — the contract is
  deliberately generic (shapes how the agent *thinks*, not a fact — **CF-N2**) and the pointer block is
  load-bearing for making the constitution discoverable. Report drift there as `keep-but-verify` and defer to
  `/context-constitution`; never trim it.

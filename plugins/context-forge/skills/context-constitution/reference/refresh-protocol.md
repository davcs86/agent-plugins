# context-forge — refresh protocol

Load this at the start of a `refresh` run. Refresh keeps an existing constitution + contract current
as the code evolves, **incrementally** — it re-derives only what changed since each target's
constitution was last written, reports drift, and applies only the deltas. It is the mode you'd run
periodically or in CI; `refresh … check` is the write-nothing linter form.

## The baseline is git — the header SHA sharpens it

Refresh keeps **no separate persisted baseline file**. Each target's diff floor is derived from git,
from two signals combined so the result is never less safe than the older one alone:

- **`R_write`** — the last commit that wrote its `context-constitution.md`:
  ```
  R_write = git log -1 --format=%H -- <target dir>/<constitutionPath>
  ```
- **`R_head`** — the commit hash recorded in that constitution's own **header provenance line**
  (`… at commit <short-sha>`), i.e. the exact repo state the last analysis actually ran against.

Resolve `R_head` to a full commit and confirm it exists in this checkout (`git rev-parse --verify
--quiet <short-sha>^{commit}`), then take the floor as the **older (common ancestor) of the two**:

```
R = git merge-base R_head R_write     # the older of the analyzed point and the last write
```

and scan `R..HEAD`. Taking the older is the safety property: a purely cosmetic edit to the
constitution advances `R_write` past real code changes, but `R_head` still points at the last commit
*actually analyzed*, so the merge-base floor never lets those changes slip the new-pattern hunt.
Normally `R_head == R_write` (the write commits the file it just analyzed), so the merge-base is just
that commit and the diff is as tight as possible.

**Fallbacks (backward-compatible — a constitution forged before the header carried a SHA simply has
no `R_head`):**
- `R_head` missing / `unknown` / not resolvable in this checkout (shallow clone, or the commit was
  rebased or GC'd away, or a force-push rewrote it) → fall back to `R = R_write` (the prior behavior,
  unchanged).
- `R_write` empty — the constitution was never committed (or doesn't exist) → no baseline: treat the
  target as a **fresh forge** (full scan via the normal scan protocol) and say so.
- Nothing in scope has a committed constitution → tell the user to run `write` first.

This stays per-target for free (each file has its own history + its own header), works in CI /
detached HEAD, and still survives **manual edits**: a hand-edit + commit advances `R_write`; if it
didn't also touch the header, `R_head` holds the last tool-analyzed point, so the merge-base simply
scans from there — wider than the manual edit alone, but always safe. The next refresh write restamps
the header to the new HEAD.

> Correctness does **not** depend on R being perfectly placed. The staleness check below validates the
> existing rules against the current code regardless of the diff window; R only *scopes the hunt for
> new patterns*. The header SHA makes R **tighter and more honest** — the real analyzed point, not a
> point a cosmetic edit shoved forward — never less safe.

## Scope

- `refresh` (no path) → every target that has a committed constitution, **plus** any newly-added
  module the scout discovers that has none yet (so new modules get picked up).
- `refresh <path>` → only the target(s) under that path, each diffed from its own git baseline.

## Phase 0′ — Diff-scoped scan

For each in-scope target `T`, resolve `R` from git as above, then:

1. **Compute the change set.** `git diff --name-only R..HEAD -- <T dir>` for committed changes, plus
   `git status --porcelain -- <T dir>` for uncommitted ones. Empty change set → mark `T` **up to
   date** for pattern purposes (still run the staleness check in step 3).
2. **Scoped scout, change-focused.** If `T` changed, spawn `convention-scout` against `T` as usual but
   pass the change set so it prioritizes new/emergent patterns, asymmetries, and contracts in or
   touching the changed files. It may still report a pattern spanning changed + unchanged sites —
   changes often *reveal* an existing invariant.
3. **Staleness check (always — this is the correctness net).** For every rule already in `T`'s
   `context-constitution.md`, verify each cited `path:line` still resolves to the referenced code (Read/Grep).
   A citation that no longer resolves flags the rule **stale**. A rule whose sites still resolve but
   whose count dropped below the induction bar (e.g. a 9/9 pattern is now 3/9) flags **weakening**.
   This runs even when the change set is empty, so drift is caught no matter where R landed.
   **Same check extends to `context-constitution-findings.md`, if `T` has one (CF-N12):** for every open
   row under Documentation-that-lies / Latent bugs / Dead-or-orphaned-code, re-resolve its citation and
   re-check its claim against current code — a doc-lie row where the code now implements the promised
   behavior (or the false doc line is gone), a latent bug whose site no longer reproduces it, or dead
   code that's since been wired up all flag **findings-resolved**. A row stays open unless its citation
   was actually re-checked and no longer holds — never resolve on an empty diff alone.
4. **Git archaeology, bounded to the window.** Run the scar hunt (scan protocol step 3) over `R..HEAD`
   only — new reverts/hotfixes since the constitution was last written — not the whole history again.

A target that is both up to date *and* has no stale/weakening rules is reported "no change" and
skipped in synthesis — do not re-emit its unchanged rules.

## Phase 1′ — Synthesize deltas (a changelog, not a rewrite)

Per changed target, produce a **delta report** rather than a whole new file:

- **Added** — new grounded rules from changed/emergent patterns (assign the *next* free IDs in the
  target's existing scheme; never renumber existing rules — **CF-4, CF-N5**).
- **Stale** — existing rules whose citations no longer resolve. Proposed action: retire, or re-ground
  to the moved code if the scout found it.
- **Weakening** — rules whose evidence thinned; proposed action: demote a tier, or keep with a note.
- **Resolved candidates** — prior `## Candidate rules (unverified)` entries the new evidence now
  grounds (promote) or refutes (drop).
- **New findings** — defects (documentation that lies, latent bugs, dead/orphaned code) the scoped
  scout surfaced from changed/emergent code, routed the same as a full scan (**CF-N9**); proposed
  action: append to `context-constitution-findings.md`'s matching open section.
- **Findings resolved** — open findings-log rows whose citation no longer reproduces the defect
  (**CF-N12**, confirmed by the staleness re-check above, never assumed); proposed action: move to
  `## Resolved`, dated, with how it was confirmed.
- **New targets** — modules discovered with no committed constitution; proposed action: full forge.

Unchanged rules are **not** touched, re-emitted, or renumbered.

## Gate

Present the delta report as an itemized changelog (per target: added / stale / weakening / resolved /
new-findings / findings-resolved / new-target), then `AskUserQuestion` (plain chat under Cursor):
**Apply deltas** / **Adjust** (edit a proposed delta and re-synthesize) / **Report only** (write
nothing).

**Non-destructive still holds, with one refinement (CF-4).** Refresh may **retire or re-ground an
existing rule only via an explicit, itemized delta the user approved at this gate** — never silently.
Absent approval for a specific stale rule, it stays as-is (optionally annotated `> ⚠ citation
unresolved as of <date>` so the staleness is visible without deleting knowledge). Additions merge as
in a normal write.

## Phase 2′ — Apply

On **Apply deltas**, per target actually written:

1. Merge the approved deltas into `context-constitution.md` (append additions; apply approved retire/re-ground
   edits; promote/drop resolved candidates). Refresh the `<!-- …:behavioral-contract… -->` block in
   place only if the behaviors or cited IDs changed. Update the header's provenance line to this run's
   ref — the date plus branch `git rev-parse --abbrev-ref HEAD` and commit `git rev-parse --short HEAD`
   — so the file records the commit this refresh reran against (metadata, not a rule, so refreshing it
   is not a CF-4 overwrite). Do the same for `context-constitution-findings.md` when this run writes it.
2. **Merge findings (CF-N12).** Append approved new-findings rows to their matching open section in
   `context-constitution-findings.md` (create it from `templates/findings.md` if this target had none
   yet). Move approved findings-resolved rows to `## Resolved`, dated, with how the re-check confirmed
   it. Then, if this apply added any *new* open rows, run one triage gate before the run ends:
   `AskUserQuestion` (options batched into groups of ≤4 — the tool's per-question cap — one option per
   new finding, `multiSelect`), asking which to dismiss now; leaving one unselected keeps it open. For
   each dismissed item, capture a one-line reason and write it straight to `## Dismissed (won't fix)`
   with the date and reason instead of its open section. Skip the gate entirely when zero new rows were
   added — don't re-litigate old open ones every run.
3. Stage this target's `context-constitution.md`, its `CLAUDE.md`, and — if this run touched it —
   `context-constitution-findings.md`. **No baseline to record** — the commit that lands this change
   *is* the new baseline (git derives it next time). This is why a manual edit and a refresh are
   indistinguishable to the next run: both are just commits to the constitution.

## `check` sub-mode (CI / scheduled linter)

`refresh <path?> check` runs Phase 0′ + Phase 1′ and **prints the delta report, then stops — no gate,
no writes.** Use it to detect a constitution (and findings log) drifting from the code: a clean run
reports "no drift" for every in-scope target; a run with additions/stale/weakening/new-findings/
findings-resolved lists them. It is the safe form to wire into CI or a schedule, since it can never
modify the repo — and since it needs no stored state, it works on any checkout.

## Guardrails

- **Git is the baseline — no side-channel state file.** Never reintroduce a separate stored
  last-forged ref. Derive the floor each run from git: the last commit that wrote the constitution
  (`git log`), taken as the older (`git merge-base`) of it and the analyzed commit recorded in the
  constitution's own header — provenance that lives *in the artifact*, not a duplicated state file,
  and only ever an augmenting floor, never the sole source of truth. When the header SHA is absent or
  unresolvable, fall back to the git-log point alone. This keeps manual edits and refreshes
  interchangeable and never trusts a ref git can't confirm.
- **Staleness is the correctness net, the diff is the optimization.** Always run the staleness check,
  even when the change set is empty.
- **Never invent (CF-1).** A "stale" flag requires a citation that actually failed to resolve, not a
  guess; a scar in the window cites its commit. Same for a **findings-resolved** flag (**CF-N12**) — it
  requires the citation to have actually been re-checked against current code, never assumed from an
  empty diff.
- **`check` writes nothing, ever.**

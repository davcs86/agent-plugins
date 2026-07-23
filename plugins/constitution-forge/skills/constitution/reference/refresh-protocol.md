# constitution-forge — refresh protocol

Load this at the start of a `refresh` run. Refresh keeps an existing constitution + contract current
as the code evolves, **incrementally** — it re-derives only what changed since each target's
constitution was last written, reports drift, and applies only the deltas. It is the mode you'd run
periodically or in CI; `refresh … check` is the write-nothing linter form.

## The baseline is git, not stored state

Refresh keeps **no persisted baseline**. Each target's "last forged" point is simply the last commit
that wrote its `constitution.md`:

```
R = git log -1 --format=%H -- <target dir>/<constitutionPath>
```

This is per-target for free (each file has its own history), survives **manual edits** (a hand-edit +
commit to the constitution advances R naturally — no config to keep in sync), and works in CI /
detached HEAD. If that git query is empty — the constitution was never committed (or doesn't exist) —
there is no baseline: treat the target as a fresh forge (full scan via the normal scan protocol) and
say so. If *nothing* in scope has a committed constitution, tell the user to run `write` first.

> Correctness does **not** depend on R being perfectly placed. The staleness check below validates the
> existing rules against the current code regardless of the diff window; R only *scopes the hunt for
> new patterns*. A purely cosmetic edit to a constitution can advance R past some code changes, so the
> new-pattern hunt might skip them — but any rule those changes broke is still caught as stale.

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
   `constitution.md`, verify each cited `path:line` still resolves to the referenced code (Read/Grep).
   A citation that no longer resolves flags the rule **stale**. A rule whose sites still resolve but
   whose count dropped below the induction bar (e.g. a 9/9 pattern is now 3/9) flags **weakening**.
   This runs even when the change set is empty, so drift is caught no matter where R landed.
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
- **New targets** — modules discovered with no committed constitution; proposed action: full forge.

Unchanged rules are **not** touched, re-emitted, or renumbered.

## Gate

Present the delta report as an itemized changelog (per target: added / stale / weakening / resolved /
new-target), then `AskUserQuestion` (plain chat under Cursor): **Apply deltas** / **Adjust** (edit a
proposed delta and re-synthesize) / **Report only** (write nothing).

**Non-destructive still holds, with one refinement (CF-4).** Refresh may **retire or re-ground an
existing rule only via an explicit, itemized delta the user approved at this gate** — never silently.
Absent approval for a specific stale rule, it stays as-is (optionally annotated `> ⚠ citation
unresolved as of <date>` so the staleness is visible without deleting knowledge). Additions merge as
in a normal write.

## Phase 2′ — Apply

On **Apply deltas**, per target actually written:

1. Merge the approved deltas into `constitution.md` (append additions; apply approved retire/re-ground
   edits; promote/drop resolved candidates). Refresh the `<!-- …:behavioral-contract… -->` block in
   place only if the behaviors or cited IDs changed.
2. Stage only this target's `constitution.md` and its `CLAUDE.md`. **No baseline to record** — the
   commit that lands this change *is* the new baseline (git derives it next time). This is why a
   manual edit and a refresh are indistinguishable to the next run: both are just commits to the
   constitution.

## `check` sub-mode (CI / scheduled linter)

`refresh <path?> check` runs Phase 0′ + Phase 1′ and **prints the delta report, then stops — no gate,
no writes.** Use it to detect a constitution drifting from the code: a clean run reports "no drift"
for every in-scope target; a run with additions/stale/weakening lists them. It is the safe form to
wire into CI or a schedule, since it can never modify the repo — and since it needs no stored state,
it works on any checkout.

## Guardrails

- **Git is the baseline — persist nothing.** Never reintroduce a stored last-forged ref; derive it
  from `git log` on the constitution file each run. This is what makes manual edits and refreshes
  interchangeable and keeps the plugin from duplicating state git already holds.
- **Staleness is the correctness net, the diff is the optimization.** Always run the staleness check,
  even when the change set is empty.
- **Never invent (CF-1).** A "stale" flag requires a citation that actually failed to resolve, not a
  guess; a scar in the window cites its commit.
- **`check` writes nothing, ever.**

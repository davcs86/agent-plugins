<!--
  Template for the findings log — the durable home for what the scan surfaced that is a DEFECT to
  fix, not an invariant to respect (CF-N9). Written as <constitutionPath dir>/context-constitution-findings.md,
  sibling to the constitution, per target (root + each module). Nothing the scout grounded is dropped
  (CF-N8): if it isn't a rule/pointer/gotcha/candidate, it lands here. Scratch mode emits it inline.
  Do not copy this comment into the output.
-->
# <Target name> — Constitution Findings

Defects and drift surfaced by `/context-constitution` (context-forge) on <ISO date | "unknown"> while
deriving the constitution — the things an agent trusting the docs or the surface would get **wrong**.
These are for triage/fixing (feed them to your issue tracker), not governance: a defect is not a rule.
Every entry cites the code. This log is maintained, not write-only (**CF-N12**): re-running
`/context-constitution refresh` re-verifies every open row below against current code and retires the
ones no longer reproducing to `## Resolved`; each run's newly-surfaced rows get a triage gate (keep
open, or dismiss with a recorded reason to `## Dismissed (won't fix)`) instead of just piling up.

> Lead with a **⚠ security** marker on any defect that affects an authz/authn/secret/tenant-isolation
> boundary (e.g. documentation that claims a validation the code doesn't perform) — those are the most
> dangerous to leave buried in aspirational docs. Order each section most-severe first.

## Documentation that lies (docs claim behavior the code lacks)

| What the docs say | What the code does | Evidence | Suggested action |
|---|---|---|---|
| <documented behavior / config key / dependency> | <not implemented / read by no code / never called> | `path:line` or "zero call sites" | fix the code, or correct the doc |

## Latent bugs (looks broken, not merely non-obvious)

| Issue | Impact | Evidence |
|---|---|---|
| <the bug> | <what breaks, for whom> | `path:line` (+ commit if a regression) |

## Dead / orphaned code

| What | Why it looks dead | Evidence |
|---|---|---|
| <module / column / config key / handler> | <nothing imports/reads/writes it> | `path:line` (+ "grep: zero call sites") |

## Open questions (unresolved *why* — needs a maintainer)

Carried over from the scout's `## Ask the human` items that a human has not yet answered. Once
answered, a "looks-wrong-but-intentional" item becomes a constitution **gotcha** (with the recorded
rationale); a "yes that's a bug" answer stays here as a latent bug.

- <observation + citation> — question: <the exact thing to ask> — status: **open**

## Dismissed (won't fix)

Findings a human triaged and chose not to action — kept for the record, never silently dropped
(**CF-N8**). A dismissal is a disposition, not a rebuttal: if a later scan re-grounds the same defect
from scratch, it is reported again rather than assumed still-dismissed.

| What the docs say / issue | Evidence | Dismissed | Reason |
|---|---|---|---|
| <original finding> | `path:line` | <ISO date> | <the human's stated reason> |

## Resolved

Findings whose citation no longer reproduces the defect, verified by `refresh`'s staleness re-check —
never assumed from an empty diff or a stale citation going unresolved.

| What the docs say / issue | Evidence (was) | Resolved | How confirmed |
|---|---|---|---|
| <original finding> | `path:line` | <ISO date> | <e.g. "code now implements it" / "doc line removed"> |

<!-- Write "_None._" under any section with no entries rather than leaving it blank. -->

---
_Surfaced by [context-forge](https://github.com/davcs86/agent-plugins). Open items above are defects to
action, not rules to keep — nothing the scan found is discarded (CF-N8); resolved and dismissed items
stay on record rather than being deleted (CF-N12). Re-run `/context-constitution refresh` to catch
newly-resolved rows and pick up new defects._

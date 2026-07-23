<!--
  Template for the findings log — the durable home for what the scan surfaced that is a DEFECT to
  fix, not an invariant to respect (CF-N9). Written as <constitutionPath dir>/constitution-findings.md,
  sibling to the constitution, per target (root + each module). Nothing the scout grounded is dropped
  (CF-N8): if it isn't a rule/pointer/gotcha/candidate, it lands here. Scratch mode emits it inline.
  Do not copy this comment into the output.
-->
# <Target name> — Constitution Findings

Defects and drift surfaced by `/constitution` (constitution-forge) on <ISO date | "unknown"> while
deriving the constitution — the things an agent trusting the docs or the surface would get **wrong**.
These are for triage/fixing (feed them to your issue tracker), not governance: a defect is not a rule.
Every entry cites the code. Refresh by re-running `/constitution`.

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

<!-- Write "_None._" under any section with no entries rather than leaving it blank. -->

---
_Surfaced by [constitution-forge](https://github.com/davcs86/agent-plugins). These are defects to
action, not rules to keep — nothing the scan found is discarded (CF-N8). Re-run `/constitution` to refresh._

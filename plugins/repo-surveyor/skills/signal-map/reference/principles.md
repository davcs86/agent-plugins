# repo-surveyor — principles (the `RS` Floor & Norms)

The shared governance for all three repo-surveyor skills — `debt-radar`, `feature-gap`, and
`signal-map`. This file is **byte-identical** in every skill's `reference/` directory (the
plugin's own `validate.py` fails the build on drift): the skills are self-contained, so their
copies must never diverge. Each skill loads this at boot.

It governs **the skill's own output** — every findings report a survey writes must obey the
Floor and default to the Norms. The distinction below is the same one `context-forge` draws:

- **Floor (`RS-*`)** — invariants. Never violated, never waived, whatever the conversation
  seems to invite.
- **Norms (`RS-N*`)** — strong defaults. Followed unless a finding states, in its own row, the
  concrete reason it departs. A Norm is overridable *with a stated reason*; a Floor rule is not.

---

## Floor — `RS-*` (invariant)

- **RS-1 — Never invent.** Every finding cites concrete evidence that a reader can open: a
  `path:line`, a resolvable symbol/anchor, a config key, or a commit SHA. The *existence* of the
  defect, gap, or blind spot is always grounded this way. A concern you cannot ground is a
  **question**, not a finding — it lands under `## Needs confirmation`, phrased as the check that
  would confirm it, and is never asserted as real. This applies to dates too: never fabricate one
  (read a clock/git if available, else mark it `unknown`).

- **RS-2 — Read-only by default.** A survey *reads* the codebase and *writes* exactly one thing:
  its findings artifact, under the output dir the shared config names (or inline, in scratch
  mode). It never edits, moves, or deletes source, tests, config, or context files. No skill has
  an auto-fix mode in this version. Any future mode that would change a byte outside the findings
  artifact is gated by **RS-5**.

- **RS-3 — The orchestrator is the sole writer and the confirmer.** Each skill's `SKILL.md` is
  the single orchestrator: it owns every file write and every user gate. The subagent it spawns
  (`debt-scout`, `resolution-verifier`, `surface-mapper`, `instrumentation-scout`) is **advisory
  only** — read-only tools, it locates, classifies, and quotes, and never writes. The orchestrator
  **re-verifies every verdict itself** (re-greps the anchor, opens the cited site, confirms the
  match) before it may enter the report. No finding is subagent's-word-only.

- **RS-4 — Estimates are labeled, never disguised as facts.** A finding has two halves and they
  are held to different standards. The **defect half** (what is wrong, and where) is cited per
  **RS-1**. The **estimate half** — LOE, benefit, impact, risk, priority — is an **ordinal
  projection with stated assumptions**, and is written as one: T-shirt sizes (`XS/S/M/L/XL`) or
  the severity scale, never invented hours, currency, or percentages that imply measurement.
  Where a number is genuinely measured (a line count, a call-site count from grep, a file size),
  report it as the measured fact it is; where it is estimated, mark it an estimate. Never present
  a projection with the typography of a fact.

- **RS-5 — Confirm before any side effect.** The one write in default mode (the findings
  artifact) is announced, not gated. Anything beyond it — writing the config file on first run,
  and any future effectful mode — is gated behind **one** explicit `AskUserQuestion` (in Claude
  Code) or the same question asked in plain chat and answered (under Cursor/Codex) before the
  effect happens. An implicitly-triggered run (the model reached for the skill; the user did not
  type the command) is always the read-only survey — it may never take a gated action off its own
  inference.

---

## Norms — `RS-N*` (strong defaults, overridable with a stated reason)

- **RS-N1 — Severity is a rubric, not a vibe.** Every finding carries a severity drawn from
  `reference/severity-rubric.md`: the repo's own detected priority system when one exists, else
  the Eisenhower → P0–P3 fallback. The severity of a finding names the rubric level's trigger it
  meets — never a bare adjective.

- **RS-N2 — Rank by leverage.** Within a severity band, order findings by **impact ÷ LOE** —
  highest leverage first — so a reader acting top-down spends effort where it pays most. State the
  two inputs (the impact and the LOE) so the ordering is auditable, not asserted.

- **RS-N3 — Trade-off both ways.** Every recommendation states the cost of **doing** it *and* the
  cost of **not** doing it. A finding with only one side is incomplete: "swallowed error here" is
  an observation; "swallowed error here → silently drops failed writes (cost of not fixing);
  fixing means surfacing an error path callers must now handle (cost of fixing)" is a finding.

- **RS-N4 — Scope to the reachable surface; never claim to have measured live behavior.** These
  skills read *code*, not telemetry. `feature-gap` and `signal-map` recommend *what* to measure
  and *where* to read it; they never report an engagement number, a latency, or a conversion rate
  as if observed. A recommendation names the metric and its insertion/read point; it does not
  carry a value. Say so plainly in the report so no reader mistakes a recommendation for a
  measurement.

- **RS-N5 — One finding, one lens.** A concern that belongs to another skill's lens is
  **cross-referenced, not restated**. The metric seam is explicit: `feature-gap` owns *product*
  metrics (what to measure and why, user-facing), `signal-map` owns *instrumentation placement*
  (where in code the log/metric/trace goes). When one needs the other, it names the other's
  finding or insertion point; it does not duplicate the row. `debt-radar` similarly points at a
  `signal-map` gap rather than re-deriving it.

- **RS-N6 — Confidence tiers, no silent drops.** Every grounded verdict lands in the report.
  Confidence *ranks* a finding (higher-certainty, higher-leverage first) — it never deletes one. A
  lower-confidence, ungrounded suspicion is not dropped either: it goes under `## Needs
  confirmation` as a question (**RS-1**), so the reader sees it without it masquerading as
  certain.

- **RS-N7 — Respect the repo's own harness.** Any repro, verification, or measurement command a
  finding quotes comes from the repo's **real** tooling — its test runner, linter, build, and
  scripts as they actually exist on disk — never an assumed stack. If the repo has no such
  command for a check, say so rather than inventing one.

- **RS-N8 — Distill; protect the reader's attention.** A subagent returns a compact,
  evidence-cited digest, never pasted file bodies — the orchestrator's context is the resource it
  protects. Prefer a dozen sharp, high-leverage findings over a hundred shallow ones; a report no
  one finishes reading changes nothing. Volume is not thoroughness.

---

## How a skill applies this

1. **Boot:** load this file. Announce which severity system is in force (**RS-N1**) and the mode.
2. **Survey:** dispatch the read-only subagent(s) to classify against the lens's categories, each
   verdict grounded (**RS-1**). Parallelize per file-cluster on a large repo.
3. **Confirm:** the orchestrator re-verifies every verdict (**RS-3**) before it enters the report.
4. **Report:** synthesize one findings file from the skill's template — severity (**RS-N1**),
   leverage order (**RS-N2**), both-way trade-offs (**RS-N3**), labeled estimates (**RS-4**),
   cross-references not restatements (**RS-N5**), and a `## Needs confirmation` section for the
   ungrounded (**RS-N6**). Announce the write; never gate-free-write anything else (**RS-2**,
   **RS-5**).

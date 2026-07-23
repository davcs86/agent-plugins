# constitution-forge — synthesis protocol (Phase 1)

Turn the Phase 0 evidence — emergent patterns, asymmetries, cross-module contracts, git scars, and
"ask the human" flags — into, per target, a `constitution.md` and a behavioral-contract block. This
is where judgment lives. You (the orchestrator) do all of it; no subagent writes.

## Step 1 — Resolve the "ask the human" flags FIRST

Before writing anything, clear the scout's `## Ask the human` list — this is where Tier-3 tribal
knowledge actually enters the file. For each flagged observation, ask the user (one
`AskUserQuestion` batching related items; plain chat under Cursor): "*Found `<observation>` at
`<path:line>` — it looks like `<anti-pattern>` but appears intentional (`<N sites>`). Is it, and
why?*" Record the answer as the rule's **rationale**. If the user doesn't know or says "it's a bug,"
it becomes a candidate or a noted cleanup — never a rule dressed up as intentional (**CF-1, CF-2**).

## Step 2 — Apply the inclusion test (the concision cut, up front)

For every candidate line, from any source, ask:

> Would a competent agent, reading only the files its task touches, **miss this** and get it wrong?

- **No** → drop it, or demote to a one-line pointer. Anything already stated in a doc the agent
  loads, enforced by a CI step, visible in the single file it would edit, or readable from a manifest
  is **out** (**CF-N4**). A constitution of restated rules is worse than none.
- **Yes** → keep it. Emergent patterns, asymmetries, cross-module contracts, and scars pass because
  they are invisible on a normal-effort read.

This cut comes *before* tiering so you never spend effort ID'ing a rule that shouldn't exist.

## Step 3 — Cluster into rules and assign a tier

Group surviving findings (two citations enforcing one intent = one rule). Tier by strength, using
the repo's own framing if it has one (**CF-N5**):

- **Floor** — non-overridable "never do" invariants a violation of which is a defect (often the thing
  a scar proves: "never edit an applied migration — PR #412 outage").
- **Rules** — binding patterns an agent must follow to fit in (the undocumented conventions,
  cross-module contracts).
- **Norms** — defaults/preferences and asymmetry guidance ("follow the `path:line` shape, not the
  `path:line` outlier").

Every rule carries: the intent, its **evidence** (multi-site citations, an authoritative site, or a
commit/PR for a scar), and — when known — a one-line **why**. The *why* is what makes it stick;
include it whenever git or the human supplied it.

## Step 4 — Ground or quarantine (CF-1)

A rule in any binding tier is grounded by real sites (N ≥ 3, or one authoritative site, or a commit).
Anything short of that goes under `## Candidate rules (unverified)` phrased as a question — never
asserted. Multi-instance induction is *not* invention; a rationale you never read *is*.

## Step 5 — Dedup up the tree (CF-N3)

Monorepo: a rule that holds repo-wide lives in the **root** constitution only. A module constitution
lists only module-specific findings and adds one line — "Inherits all root constitution rules
(`<root path>`)." Cross-module contracts live at the **root** (they are about the seams between
modules, not inside one). Before writing a module rule, confirm it isn't already a root rule.

## Step 6 — Build the behavioral contract

Same four behaviors for every repo (that portability is the point). Wrap in sentinel markers so
re-runs replace in place. Canonical block:

```markdown
<!-- constitution-forge:behavioral-contract:start -->
## How to Act

Read this first — it governs *how* you work here; everything below is the *what* you work with.
These four behaviors are the operating defaults; the rest of this file (and the constitution) is
context you load per task.

1. **Don't assume — ask, and surface tradeoffs.** On ambiguity, a missing detail, or a design fork,
   stop and raise it; never paper over it with a silent guess.
2. **Write the minimum that solves the stated problem.** Nothing speculative — no abstraction,
   option, or "while I'm here" scaffolding the task didn't ask for. Would a senior engineer call it
   overbuilt for what was requested? Then simplify.
3. **Touch only what the task requires.** Keep diffs surgical and auditable; clean up orphans *you*
   introduced, but don't reformat or "improve" code nobody asked you to touch.
4. **Define success up front, then loop until verified.** State the pass condition before you start,
   then run to it — write the check, run it, fix, re-run — and don't declare victory mid-loop.

> Litmus test for any future line in this file: *does it shape how the agent thinks (a behavior), or
> restate a fact the agent can read from the code?* If it's a fact already in the repo, leave it out.
<!-- constitution-forge:behavioral-contract:end -->
```

**Citation variant (`citeIds: true`).** When this target produced a constitution, append to each
behavior a short pointer to the IDs that enforce it — anchoring the generic principle to the local,
hard-won rules. Only cite IDs you actually generated for this target (or the root, for an inheriting
module). Never cite an ID that doesn't exist (**CF-1**). If `citeIds` is off or the target has no
constitution, use the generic block unchanged.

## Step 7 — Assemble each constitution

Fill `templates/constitution.md`: a one-paragraph preamble (what this target is, that the file
captures the *non-obvious* — patterns, contracts, scars — not restated docs), the tiered rule tables
with evidence + why, a `## Gotchas & scars` section for the Tier-3 items, the `## Candidate rules
(unverified)` section (or "none"), and the footer. When merging into an existing file, keep every
existing rule and ID verbatim (**CF-4**); only append.

Then present everything at the Phase 1 gate (targets, rule counts by tier, candidate count, the
contract block + prepend preview).

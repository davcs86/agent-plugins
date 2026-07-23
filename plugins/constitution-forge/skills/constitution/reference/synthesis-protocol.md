# constitution-forge — synthesis protocol (Phase 1)

Turn the Phase 0 evidence digests into, per target, a `constitution.md` and a behavioral-contract
block. This is where judgment lives — clustering, tiering, dedup, and the concision cut. You (the
orchestrator) do all of it; no subagent writes.

## Step 1 — Cluster evidence into rules

Group the digest's citations into distinct rules. Two citations that enforce the same intent (a
prose "always run the linter" + the CI lint step) become **one** rule citing both. A rule is one
enforceable intent, not one sentence.

## Step 2 — Assign a tier

Three tiers, strongest first. Use the repo's own framing when it has one (**CF-N5**); otherwise:

- **Floor** — non-overridable, "never do" invariants where a violation is a defect: "never edit an
  applied migration", "never push to `main`", "never commit secrets", "never exceed the connection
  budget". A Floor rule usually maps to something CI or infra *hard-fails* on.
- **Rules** — binding conventions the repo expects followed: naming schemes, required test/coverage,
  header propagation, proto/lint gates, branch/PR flow. Overridable only with a recorded reason.
- **Norms** — defaults and preferences: "prefer enums over strings", "reuse over rebuild", style
  leanings. Waivable at judgment.

## Step 3 — Assign IDs

Give each rule a stable `<PREFIX>-NN`. Derive `<PREFIX>` from the target: root → a repo token
(e.g. the repo name's initials); module → the module name (e.g. `TRADING-01`). **If the target
already has an ID scheme, extend it — never renumber or re-prefix existing rules (CF-N5, CF-4).**
IDs are what the behavioral contract and future reviews cite, so they must be stable across re-runs.

## Step 4 — Evidence gate (CF-1)

Every rule in a binding tier cites `path:line`. A rule you believe is true but found no evidence for
does **not** go in a tier — it goes under `## Candidate rules (unverified)` with a note on why you
suspect it and what would confirm it. The user promotes candidates to real rules at the gate, or
drops them. Never assert a candidate as binding.

## Step 5 — Dedup up the tree (CF-N3)

For a monorepo: any rule that holds repo-wide belongs in the **root** constitution only. A module
constitution lists module-specific rules and adds one line — "Inherits all root constitution rules
(`<root path>`)." — instead of restating them. Before writing a module rule, check it is not already
a root rule; if it is, drop it from the module.

## Step 6 — Concision cut (CF-N4)

Apply the litmus test to every line, in both the constitution and the contract: *would removing it
cause a mistake the agent couldn't recover from, or does it just restate a fact readable from the
code?* Cut architecture the agent can read, style it can infer, and dependency lists already in a
manifest. A short, dense constitution beats a long, padded one.

## Step 7 — Build the behavioral contract

The contract is the same four behaviors for every repo (that portability is the point). Wrap it in
sentinel markers so re-runs replace it in place. Canonical block:

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
behavior a short pointer to the IDs that enforce it — the specialization that turns a generic
principle into a locally-anchored one. Example, using generated IDs:

> 1. **Don't assume — ask, and surface tradeoffs.** … (enforced by **XS-02** and the design gate.)
> 4. **Define success up front, then loop until verified.** … (enforced by **XS-07** test-pairing,
>    **XS-09** "never commit before verification passes".)

Only cite IDs that exist in the constitution you just synthesized for this target (or the root, for a
module whose behaviors are enforced by inherited rules). Never cite an ID you did not generate
(**CF-1**). If `citeIds` is off, or the target has no constitution, use the generic block unchanged.

## Step 8 — Assemble each constitution

Fill `templates/constitution.md`: a one-paragraph preamble naming the target and how the file was
derived, the tiered rule tables, the `## Candidate rules (unverified)` section (or "none"), and a
footer noting it was forged by `/constitution` and should be refreshed by re-running it. Keep the
existing file's rules verbatim when merging (**CF-4**).

Then present everything at the Phase 1 gate.

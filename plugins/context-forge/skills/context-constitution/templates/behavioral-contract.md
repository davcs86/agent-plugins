<!--
  The behavioral-contract block prepended to a target's CLAUDE.md. The sentinel markers are load-
  bearing: on re-run the skill finds this exact start/end pair and replaces the block in place,
  so a re-run never stacks a second copy. Do not remove or edit the markers by hand.

  This file is the SINGLE SOURCE of the contract block — synthesis-protocol.md Step 6 points here
  rather than re-inlining it, so the two never drift. Two forms: the generic block below (citeIds:false,
  or no constitution for this target) and the cited variant (citeIds:true) where each behavior gains a
  "(enforced by <IDS>)" tail; those citation tails are defined in reference/synthesis-protocol.md Step 6.
-->
<!-- context-forge:behavioral-contract:start -->
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
<!-- context-forge:behavioral-contract:end -->

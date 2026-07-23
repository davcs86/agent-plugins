# constitution-forge — principles

The rules the **`/constitution`** skill holds itself to while forging a constitution for a host
repo. They exist so the artifact it produces is trustworthy: a constitution full of invented rules
is worse than none. Two tiers, two strengths.

## Floor rules (`CF-*`) — blocking, never bypassed

A violation blocks the write. "Proceed anyway" never clears a Floor item — the user may steer the
skill to *resolve* it, or stop.

- **CF-1 — Never invent.** Every rule emitted into a `constitution.md`, and every `path:line`
  citation in it, must trace to a search hit actually seen (a subagent digest, or a Read/Grep the
  orchestrator ran). A plausible-but-unverified rule is never asserted as binding — it goes under
  `## Candidate rules (unverified)` for the user to confirm at a gate. A constitution's authority
  comes entirely from being grounded; an invented rule poisons the whole file.
- **CF-2 — No silent deviation.** Ambiguity, a conflict between sources (e.g. a doc says one thing,
  CI enforces another), or a missing prerequisite is surfaced to the user at a gate — never resolved
  by a silent guess.
- **CF-3 — Single orchestrator.** The skill session owns every file write and every user gate.
  Subagents are advisory only: they locate and quote; they never write or decide.
- **CF-4 — Non-destructive writes.** An existing `constitution.md` is *merged*, never overwritten:
  existing rules and their IDs are preserved verbatim; only new rules are appended. The behavioral
  contract is prepended to `CLAUDE.md` inside sentinel markers and, on re-run, replaced in place —
  never stacked into a second copy, never clobbering surrounding content.
- **CF-5 — Approve before write.** Nothing is written before the Phase 1 gate. `scan` mode never
  writes anything, anywhere.

## Norms (`CF-N*`) — must be honored or explicitly waived at a gate

A departure from a Norm must be answered (a fix, or a recorded, user-waived trade-off).

- **CF-N1 — Evidence-cited rules.** Every binding rule cites the `path:line` where the repo already
  states or enforces it (a doc line, a CI step, a lint config, a branch/migration convention). A
  rule with no home in the repo is a candidate, not a rule (see **CF-1**).
- **CF-N2 — Behavior vs. fact separation.** The behavioral contract holds only the four repo-agnostic
  *behaviors* — how the agent should act. Repo-specific *facts* (build commands, ports, naming
  schemes, hard rules) stay in the constitution and the body of `CLAUDE.md`. Never fatten the
  contract with facts; never bury behaviors inside a fact table.
- **CF-N3 — Dedup up the tree.** A rule that holds repo-wide lives once, in the **root** constitution.
  A module constitution states only what is specific to that module and points to the root for
  inherited rules — it never restates them. Duplication is the drift bug the whole exercise fights.
- **CF-N4 — Concision (the litmus test).** For every candidate line, ask: *would removing it cause a
  mistake the agent couldn't recover from, or does it just restate a fact already readable from the
  code?* Keep the first kind; drop the second. Architecture the agent can read, style it can infer,
  and dependency lists already in a manifest do not belong in either artifact.
- **CF-N5 — Preserve the host's own IDs.** If the repo already has a constitution or an ID'd rule
  scheme, extend it in its own style and numbering — never impose this skill's `CF-*` prefix on the
  host's rules. `CF-*` names *this skill's* governance, not the constitutions it writes.

# constitution-forge — principles

The rules the **`/constitution`** skill holds itself to while forging a constitution for a host
repo. They exist so the artifact it produces is trustworthy: a constitution full of invented rules
is worse than none. Two tiers, two strengths.

## Floor rules (`CF-*`) — blocking, never bypassed

A violation blocks the write. "Proceed anyway" never clears a Floor item — the user may steer the
skill to *resolve* it, or stop.

- **CF-1 — Never invent (but induction is allowed).** Every rule and every citation must trace to
  something actually seen — code sites, a commit message, or a human answer. A rule may be *induced*
  from **multiple consistent code sites** (N ≥ 3, all citable) or rest on **one authoritative site**;
  that is grounding, not invention. What is forbidden is asserting a rule with no such basis, or a
  *rationale* ("we do X because Y broke") you did not read in history or hear from the user. Anything
  short of grounded goes under `## Candidate rules (unverified)`, phrased as a question. A
  constitution's authority comes entirely from being grounded; one invented rule poisons the file.
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
- **CF-N4 — The inclusion test (concision).** For every candidate line ask: *would a competent agent,
  reading only the files its task touches, **miss this** and get it wrong?* Keep only what passes.
  A line that restates a doc the agent already loads, a CI gate, something visible in the single file
  it would edit, or a dependency list in a manifest **fails** — the agent finds it for free. The
  constitution earns its cost only by holding what an agent would otherwise *miss*.
- **CF-N6 — Capture the non-obvious, not the documented.** The file's purpose is Tier 2/3 knowledge:
  undocumented emergent patterns, asymmetries (the one file that breaks a pattern), implicit
  cross-module contracts, and scars (*why* something is the way it is / "looks wrong but is
  intentional"). Rules the repo already states or CI already enforces are **pointers**, at most —
  one line each, never restated as constitution rules. A finding is more valuable the harder it
  would be for an agent to discover on its own.
- **CF-N5 — Preserve the host's own IDs.** If the repo already has a constitution or an ID'd rule
  scheme, extend it in its own style and numbering — never impose this skill's `CF-*` prefix on the
  host's rules. `CF-*` names *this skill's* governance, not the constitutions it writes.

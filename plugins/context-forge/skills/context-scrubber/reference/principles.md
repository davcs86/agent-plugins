# context-forge — principles

The shared governance the **context-forge** skills hold themselves to. `/context-constitution` obeys them
while *forging* a constitution (adding high-signal context); `/context-scrubber` obeys them while *auditing*
context files (finding low-signal content to remove). They exist so every artifact these skills produce is
trustworthy: a constitution full of invented rules — or a scrub that deletes load-bearing context — is worse
than none. `CF-*` reads as **Context Forge**; the same IDs govern both skills, so an objection or a gate
decision in either can point at a precise rule instead of re-deriving it. Two tiers, two strengths.

> How to read these across the two skills: where a rule says "constitution," the constitution skill applies it
> to the file it writes and the scrubber applies it to the files it audits. The litmus test (**CF-N4**) is the
> hinge — the constitution skill runs it forward (*keep only what an agent would miss*), the scrubber runs it in
> reverse (*flag what an agent would find for free*).

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
- **CF-4 — Non-destructive writes.** An existing `context-constitution.md` is *merged*, never overwritten:
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
- **CF-N5 — Preserve the host's own IDs — but only extend a scheme of the *same kind*.** If the repo
  already has a constitution or ID'd rule scheme, extend it in its own style and numbering rather than
  imposing this skill's `CF-*` prefix. **However**, only fold new rules into an existing scheme when it
  governs the *same kind* of rule. If the host's scheme is, say, a process/workflow constitution
  (review gates, branch policy) and you are deriving *codebase invariants* (runtime contracts, pool
  budgets, alignment rules), do **not** renumber into it — that conflates two different rule families.
  Use a clearly-labeled **sibling namespace** (e.g. `PLAT-*` for the repo, `<MODULE>-*` per module) and
  cross-reference the existing IDs where they overlap. `CF-*` names *this skill's* governance, never
  the constitutions it writes.
- **CF-N6 — Capture the non-obvious, not the documented.** The file's purpose is Tier 2/3 knowledge:
  undocumented emergent patterns, asymmetries (the one file that breaks a pattern), implicit
  cross-module contracts, and scars (*why* something is the way it is / "looks wrong but is
  intentional"). Rules the repo already states or CI already enforces are **pointers**, at most —
  one line each, never restated as constitution rules. A finding is more valuable the harder it
  would be for an agent to discover on its own.
- **CF-N7 — Library usage is judged as deviation vs. default.** A finding about how the repo uses a
  third-party library earns a rule only if it **deviates** from the library's documented default
  (a custom setting, a non-obvious option, a documented workaround); usage that matches the docs is
  something an agent can look up and is a pointer at most. When a documentation-lookup tool (e.g.
  Context7) is available, use it to make this call (the constitution skill's library-doc protocol);
  when it isn't, fall back to consistency-based judgment — the integration is optional and never
  blocks a run.
- **CF-N8 — No silent drops (capture everything we paid to find).** A scan costs real tokens, so
  nothing a scout grounded is ever discarded. Every finding lands in a durable home: a tiered rule, a
  `## Pointers` line, a `## Gotchas & scars` entry, a `## Candidate rules (unverified)` row, or the
  **findings log** (**CF-N9**). The inclusion test (**CF-N4**) and severity decide *where* a finding
  goes and how prominently — never *whether* it survives. "Low severity" means "rank it lower / make it
  a Norm," never "delete it."
- **CF-N9 — Invariant vs. defect: route, don't enshrine.** Separate a property to **respect** from a
  property to **fix**. An invariant (looks-wrong-but-intentional, a write-dead column, an ordering or
  alignment contract) is a constitution rule or gotcha. A **defect** — a latent bug, dead/orphaned
  code, an unused config key, or **documentation that describes behavior the code does not have** — is
  NOT a rule (you don't govern "the audit route has an auth gap"); it goes to the **findings log**
  (`context-constitution-findings.md`, sibling to the constitution) with its `path:line`/commit citation and a
  suggested action, so it is actioned rather than frozen into governance. Both are durable outputs;
  neither is dropped.
- **CF-N10 — Validate a cross-cutting quirk against its owner before enshrining it.** A pattern
  observed from the *consumer* side can be an invariant to respect **or** a bug to fix, and you cannot
  tell from the consumers alone. Before recording a cross-service "quirk" as a rule, check the
  **producing/owning** module (the service that defines the contract, type, or value). If the owner's
  contract *contradicts* the observed quirk — the producer supports the correct behavior and the
  consumers get it wrong — it is a **defect** (findings log, **CF-N9**), not an invariant, even when
  many consumers share it. (Benchmark example: a "treat 0 as unset" quirk seen across consumer services
  looked like a rule, but the producing service's `oneof` contract *supported* distinguishing 0 — so
  the consumers had a bug, not the platform a convention.) Confirming a contract from **both** the
  producer and a consumer is the strongest grounding; a one-sided cross-module claim is weaker.
- **CF-N11 — Make the constitution discoverable; don't duplicate the generic contract.** Only the
  auto-loaded `CLAUDE.md` pulls context into an agent's window — a `context-constitution.md` that no `CLAUDE.md`
  references is **inert**. So every target's `CLAUDE.md` carries a one-line **pointer** to its own
  constitution (and findings), added to the host's what-to-read index if it has one. The behavioral
  **contract**, by contrast, is generic and `CLAUDE.md` loads root-downward, so it belongs in the
  **root `CLAUDE.md` only** — an identical copy in every module is exactly the duplication **CF-N3**/
  **CF-N4** fight. A per-module contract is justified *only* when `citeIds` makes it genuinely
  module-specific (it cites that module's constitution IDs); an identical generic copy never is.

# constitution-forge — scan protocol (Phase 0)

Goal: gather the **non-obvious** knowledge a constitution is built from — the patterns, asymmetries,
contracts, and scars an agent would miss on a normal read — without loading whole files into the
orchestrator. You spawn read-only scouts and run git archaeology yourself; you keep the digests, not
the file bodies. Nothing here writes.

## What you are hunting (and what you are NOT)

The value of a constitution is inversely proportional to how easily an agent would find the same
thing on its own. So the scan targets **Tier 2 and Tier 3** knowledge and deliberately demotes
Tier 1:

| Tier | What | Treatment |
|---|---|---|
| **1 — Stated & enforced** | rules in docs, gates in CI/lint | **pointer only** — one line, never a restated rule (fails the litmus) |
| **2 — Latent/emergent** | patterns followed across many files with no doc; the one file that breaks a pattern; implicit cross-module contracts | **the core of the file** — grounded in multi-site citations |
| **3 — Rationale & scars** | *why* something is the way it is; "looks wrong but is intentional"; what broke before | **highest value** — from git history + asking the human |

The inclusion test for every finding: *would a competent agent, reading only its task's files, miss
this and get it wrong?* If no, it doesn't belong.

A finding can also be a **defect** rather than an invariant — documentation that lies (behavior/config
the docs promise but the code lacks), a latent bug, or dead code. The scout surfaces these too (its
`## Documentation drift & dead code` section); synthesis routes them to the **findings log**, not the
constitution (**CF-N9**), and nothing grounded is ever dropped (**CF-N8**). A scan costs tokens — every
finding earns a durable home.

## Procedure

1. **One root scout.** Spawn `convention-scout` (Agent tool) against the analysis root. It returns
   emergent patterns (with the *wrong default* each prevents), asymmetries, cross-module contracts,
   "ask the human" flags, Tier-1 pointers, and the module map — all grounded per the agent's evidence
   rule (N ≥ 3 sites, or one authoritative site). See its output format in the agent file.

2. **Monorepo?** From the module map + workspace markers, decide. If more than one module → read
   `reference/monorepo-protocol.md` and follow it (parallel per-module scouts + a root pass whose
   special focus is cross-module contracts). Otherwise the single digest feeds Phase 1.

3. **Git archaeology (you run this — the scout can't).** With your allowed git tools, recover Tier-3
   scars the code alone can't show. Keep it bounded — a handful of targeted queries, not a full log:
   - `git log --oneline` filtered for `revert`, `hotfix`, `fix:`, `regression`, `rollback` — each is
     a candidate scar; read the message (`git show`) for the *why*.
   - For any file the scout flagged as an asymmetry or "looks-wrong", `git log -n 5 --oneline <file>`
     and read the commit that introduced the oddity — its message often *is* the rationale.
   - A recovered scar cites the **commit SHA / PR** as its evidence. If history is shallow
     (`git rev-parse --is-shallow-repository` = true), say so — note in the digest that scar
     recovery was limited and, if it matters, offer to `git fetch --unshallow`. Never invent a
     rationale you didn't read (**CF-1** covers commit messages too).
   - **Incomplete-fix check.** For each fix scar, ask whether the same bug class exists at *sibling
     sites the fix didn't touch* — a parity fix applied to one read path but not its twins, an
     encoding fix applied outbound but not inbound. An unpatched sibling is a **latent bug** for the
     findings log (**CF-N9**), and it's high-value precisely because the closed PR reads as "done."
     (Benchmark: a positions-parity fix left three other paths recomputing the wrong way; a camelCase
     fix corrected the outbound path but not the inbound one.)

4. **Detect merge targets.** For each target dir, note whether a `CLAUDE.md` and `constitution.md`
   already exist (the scout reports these) — inputs to synthesis, not overwrite targets.

5. **Do not synthesize yet.** Phase 0 only gathers. Clustering, the inclusion cut, tiering, and the
   human-Q&A gate happen in Phase 1, once the whole evidence set is in hand.

## Guardrails

- **Read-only.** The scout has Glob/Grep/Read only. You run only read/inspect git and shell. Nothing
  in Phase 0 changes the repo.
- **Distill, don't dump.** Digests are findings + citations, never file bodies.
- **Grounded beats plausible.** A pattern "every repo has" that this one doesn't actually follow is a
  candidate at most. A rationale you didn't read in a commit or hear from the human is a *question*,
  not a rule.

# constitution-forge — scan protocol (Phase 0)

Goal: gather the **evidence** a constitution is built from, without loading whole files into the
orchestrator. You spawn read-only scouts; they return compact digests; you keep the digests, not the
file bodies. Nothing here writes.

## What a rule *is* (so the scout knows what to collect)

A constitution rule is a statement the repo already makes or enforces about how work is done. The
scout hunts these evidence classes — each is a `path:line` citation waiting to happen:

1. **Stated hard rules** — absolute imperatives in convention files: "never …", "always …", "must
   (not) …", "do not …", "required", "forbidden". Sources: `CLAUDE.md` (root and nested), `AGENTS.md`,
   `CONTRIBUTING*`, `docs/` (architecture / conventions / patterns / ADRs), `.github/` templates.
   Quote verbatim + cite; never soften or harden.
2. **CI-enforced checks** — anything a pipeline fails on is a *de facto* rule even if no prose states
   it: required lint, format, type-check, coverage thresholds, `buf breaking`, schema/migration
   checks, "must be green" gates. Sources: `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`,
   `.circleci/`, pre-commit hooks (`.husky/`, `.pre-commit-config.yaml`).
3. **Encoded conventions** — rules living in config rather than prose: lint/format configs, branch
   protection / naming, migration naming + "never edit an applied migration", commit conventions,
   codeowners, dependency/version pins, connection/resource budgets.
4. **Structural invariants** — a naming scheme or layout the repo clearly holds to (env-var prefixes,
   config-key shapes, port assignments, directory-per-service). Only collect these when the repo
   *states* them or they are unambiguous across many instances — otherwise they are candidates, not
   rules (**CF-1**).

Anything expected but absent is reported under `## Not found`, never guessed.

## Procedure

1. **One root scout.** Spawn `convention-scout` (Agent tool) against the analysis root with the four
   evidence classes above and a request for the **module map**. It returns the Repo Profile digest
   (its output format is defined in the agent file).
2. **Decide monorepo vs. single module** from the digest's module map and workspace markers. If more
   than one module → read `reference/monorepo-protocol.md` and follow it (parallel per-module scouts
   + root pass). Otherwise the single root digest is your only input to Phase 1.
3. **Detect merge targets.** For each target dir, note whether a `CLAUDE.md` and a `constitution.md`
   already exist (the scout reports these). They are inputs to synthesis (dedup, merge), not things
   to overwrite.
4. **Do not synthesize yet.** Phase 0 only gathers. Clustering, tiering, and dedup happen in Phase 1
   so the whole evidence set — every module + root — is in hand before any rule is written.

## Guardrails

- **Read-only.** The scout has no Write/Edit/Bash-mutation tools; you (the orchestrator) run only
  read/inspect Bash. Nothing in Phase 0 changes the repo.
- **Distill, don't dump.** Digests are names, paths, one-line roles, and quoted rules with citations
  — never pasted file bodies. The orchestrator's context window is the resource being protected.
- **Evidence beats plausibility.** A rule "every mature repo has" but this one does not state or
  enforce is a candidate at most. The scan reports what *is*, not what *ought to be*.

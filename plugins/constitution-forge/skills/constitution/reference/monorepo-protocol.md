# constitution-forge — monorepo protocol

Load this only when Phase 0 detects more than one module. A monorepo gets **one constitution per
module, plus one repo-wide constitution at the root** — and a behavioral contract prepended to each
module's `CLAUDE.md` and the root's. This mirrors how a well-run monorepo already works: shared law
at the root, thin module docs that state only what is local.

## What counts as a module

A module is an independently-meaningful unit with its own build/test surface. Detect from (in order
of confidence):

1. **Workspace manifests** — members of `pnpm-workspace.yaml` / `package.json#workspaces`,
   `go.work` `use` entries, Cargo `[workspace] members`, `nx.json` / `turbo.json` / `lerna.json`
   project lists.
2. **Per-directory manifests** — a `package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, etc.
   one or two levels down (e.g. under `services/`, `packages/`, `apps/`, `plugins/`, `libs/`).
3. **A per-module convention doc** — a directory that already carries its own `CLAUDE.md` /
   `README.md` stating local rules is a module even if its manifest is shared.

If the signals disagree, surface the ambiguity at the Phase 1 gate (**CF-2**) with the candidate
module list — do not silently pick one.

## Procedure

1. **Enumerate modules** from the root scout's module map. Cap the parallel fan-out at a sane width
   (≈8 scouts at once); if there are more modules, batch them and say so — never silently analyze a
   subset (report any module you skipped, **CF-1** honesty).
2. **One scoped scout per module, in parallel.** Spawn `convention-scout` per module (Agent tool,
   all in one message) with the module's directory as its analysis root. Each returns a
   module-scoped digest: local hard rules, local CI (if the module has its own), local conventions,
   and — importantly — which of its "rules" are really *inherited* from the root (the scout flags a
   rule it sees stated at the root, so synthesis can dedup).
3. **Treat the root as one more target — with a special focus on the seams.** The root scout's
   digest, minus everything that clearly belongs to a single module, is the evidence for the **root**
   constitution: cross-cutting rules (branch strategy, repo-wide CI, shared resource budgets) **and
   especially cross-module contracts** — the implicit expectations one module places on another
   (headers/context a caller must forward, a seeded/shared resource that must not be mutated, a value
   that must stay in parity across read paths). These live at the root because they are about the
   space *between* modules, and their violation causes the nastiest cross-cutting rework.
4. **Synthesize per target, root-first (Phase 1).** Build the **root** constitution first so its IDs
   exist, then each module constitution — each stating only module-specific rules and *pointing to*
   the root for inherited ones (**CF-N3**). A module constitution that would just re-list root rules
   is wrong; it should be short.

## Placement

- Each module's constitution goes at `<module>/<constitutionPath>`; its contract prepends to
  `<module>/CLAUDE.md` (created if absent).
- The root constitution goes at `<root>/<constitutionPath>`; its contract prepends to
  `<root>/CLAUDE.md`.
- A module with genuinely no local rules (everything inherited) gets **no** module constitution —
  only its `CLAUDE.md` contract, whose behaviors cite the root constitution's IDs. Don't manufacture
  a hollow file to be symmetrical (**CF-N4**).

## Gate presentation

At the Phase 1 gate, show the target tree explicitly, e.g.:

```
root                → docs/constitution.md   (Floor 3 · Rules 6 · Norms 4) · CLAUDE.md contract: update
services/trading    → docs/constitution.md   (Rules 2 · Norms 1)          · CLAUDE.md contract: create
services/ledger     → (inherits root only)                                 · CLAUDE.md contract: create
packages/proto      → docs/constitution.md   (Floor 1 · Rules 3)          · CLAUDE.md contract: update
```

so the user approves the whole shape in one decision, then all writes happen in Phase 2.

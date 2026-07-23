<!--
  Template for a forged constitution. The orchestrator fills the placeholders and removes any
  empty section. Keep it dense. Every rule is grounded (multi-site citations, one authoritative
  site, or a commit/PR) and — where known — carries a one-line *why*. Do NOT restate rules the repo
  already documents or CI enforces; those are pointers at most. Do not copy this comment into output.
-->
# <Target name> — Constitution

Derived by `/context-constitution` (context-forge) on <ISO date | "unknown">. This file captures the
**non-obvious** — patterns this <repo|module> follows but never wrote down, the places that break
those patterns, the contracts between modules, and the scars behind them — the things an agent would
otherwise miss and get wrong. It does **not** restate what the docs already say or CI already
enforces (see `## Pointers`). Refresh by re-running `/context-constitution`.

<!-- Monorepo module only — keep this line, drop for a standalone/root constitution: -->
> Inherits all rules of the root constitution (`<relative path to root constitution>`). This file
> lists only what is specific to **<module name>**.

## Floor (`<PREFIX>-*`) — never-do, non-overridable

| ID | Rule | Why | Evidence |
|---|---|---|---|
| **<PREFIX>-01** | <the invariant> | <one line — often a scar> | `path:line`×N / commit / PR |

## Rules (`<PREFIX>-*`) — binding, easy-to-miss conventions

| ID | Rule | Why | Evidence |
|---|---|---|---|
| **<PREFIX>-NN** | <the undocumented convention or cross-module contract> | <why it holds> | `path:line`, `path:line`, … |

## Norms (`<PREFIX>-*`) — defaults & asymmetry guidance

| ID | Norm | Why | Evidence |
|---|---|---|---|
| **<PREFIX>-NN** | <the default; or "follow X's shape, not the Y outlier"> | <rationale> | `path:line` (norm) vs `path:line` (outlier) |

## Gotchas & scars

Tier-3 knowledge that isn't a rule so much as a landmine map — *why* a thing that looks wrong is
intentional, and what broke when someone "fixed" it. Each cites the code and the commit/PR/human
answer it came from.

- **<gotcha>** — <the trap, and the wrong move it prevents>. Evidence: `path:line` + <commit/PR>.
- (or "_None recovered._")

## Candidate rules (unverified)

Plausible but not yet grounded — confirm or drop before treating as binding.

| Candidate | Why suspected | What would confirm it |
|---|---|---|
| <candidate> | <signal> | <the sites / commit / person that would ground it> |

## Pointers (already documented or CI-enforced — not restated here)

| What | Where |
|---|---|
| <stated rule or CI gate> | `path:line` |

<!-- Write "_None._" under any section with no entries rather than leaving it blank. -->

---
_Forged by [context-forge](https://github.com/davcs86/agent-plugins). It captures the
non-obvious — nothing here is invented; re-run `/context-constitution` to refresh after the code changes._

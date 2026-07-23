<!--
  Template for a forged constitution. The orchestrator fills the placeholders and removes any
  empty tier. Keep it dense; every rule cites path:line. Do not copy this comment into the output.
-->
# <Target name> — Constitution

Derived by `/constitution` (constitution-forge) from this <repo|module>'s stated conventions, CI
gates, and encoded config on <ISO date | "unknown">. Every rule cites where it already lives —
this file indexes and ranks rules that already govern the code, it does not invent new ones. Refresh
by re-running `/constitution`.

<!-- Monorepo module only — keep this line, drop for a standalone/root constitution: -->
> Inherits all rules of the root constitution (`<relative path to root constitution>`). This file
> lists only what is specific to **<module name>**.

## Floor (`<PREFIX>-*`) — never-do, non-overridable

| ID | Rule | Evidence |
|---|---|---|
| **<PREFIX>-01** | <verbatim-or-tight paraphrase of the invariant> | `path:line` (+ CI `path:line`) |

## Rules (`<PREFIX>-*`) — binding conventions

| ID | Rule | Evidence |
|---|---|---|
| **<PREFIX>-NN** | <the convention> | `path:line` |

## Norms (`<PREFIX>-*`) — defaults, waivable with reason

| ID | Norm | Evidence |
|---|---|---|
| **<PREFIX>-NN** | <the default/preference> | `path:line` |

## Candidate rules (unverified)

Plausible rules found without firm evidence — confirm or drop before treating as binding.

| Candidate | Why suspected | What would confirm it |
|---|---|---|
| <candidate> | <signal> | <the doc line / CI step / config that would ground it> |

<!-- Write "_None._" under any section with no entries rather than leaving it blank. -->

---
_Forged by [constitution-forge](https://github.com/davcs86/agent-plugins). Rules are indexed from
the repo, not invented — re-run `/constitution` to refresh after conventions change._

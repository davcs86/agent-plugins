---
type: llm
focus: last_message
weight: 2
---

PASS if the reply is a user-facing-surface report that:
- cites at least one concrete `path:line` in `src/routes.js` as evidence;
- identifies **either** the missing delete capability (a feature gap: create + list exist, no
  delete) **or** the undocumented `purge` command (low discoverability: no description / absent from
  `--help`);
- assigns a **severity**; and
- frames its metric suggestions as **recommendations** (what to measure), not observed values.

FAIL if it reports a live/observed engagement or usage number as if measured, edits code, or cites
nothing.

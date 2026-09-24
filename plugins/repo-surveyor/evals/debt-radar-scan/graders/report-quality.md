---
type: llm
focus: last_message
weight: 2
---

PASS if the reply is a technical-debt findings report that:
- cites at least one concrete `path:line` as evidence (e.g. `src/sample.py:NN`);
- identifies the **swallowed exception** in `src/sample.py` (the empty `except` that silently
  ignores a failed config read);
- assigns a **severity** to findings; and
- states **both** the cost of fixing and the cost of not fixing for at least one finding.

Also credit flagging the dead `_unused_legacy_helper` function.

FAIL if it invents findings with no citation, edits or rewrites the code, or omits severity.

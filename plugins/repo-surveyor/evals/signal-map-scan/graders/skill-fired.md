---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?signal-map"'
arm: with-only
---

Passes when the `signal-map` skill was invoked (bare or `plugin:`-namespaced).

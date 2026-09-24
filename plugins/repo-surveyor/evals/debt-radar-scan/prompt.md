---
name: debt-radar-scan
description: debt-radar flags a swallowed error and dead code, cited, in read-only scratch mode
tags: [smoke, debt-radar]
plugins: ["../.."]
runs: 2
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill, Task]
expected_outcome: An inline technical-debt report citing src/sample.py, flagging the swallowed except and the dead helper, with severity and both-way trade-offs; no files written.
---

This repository has a small Python module under `src/`. Use the repo-surveyor **debt-radar** skill
to survey it for technical debt.

Run in scratch mode and present the findings report **inline** in your reply — do not write any
files. For each finding, give the cited evidence (a `path:line`), a severity, the benefit of
fixing, and the trade-off both ways (the cost of fixing and the cost of not fixing).

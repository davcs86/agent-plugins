---
name: signal-map-scan
description: signal-map flags the unlogged external-call failure branch with a signal type, cited, read-only
tags: [smoke, signal-map]
plugins: ["../.."]
runs: 2
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill, Task]
expected_outcome: An inline instrumentation report citing src/fetcher.py, recommending a signal (log/metric/span) on the silent except branch with the question it answers, marked recommendation-only; no files written.
---

This repository has a service module under `src/`. Use the repo-surveyor **signal-map** skill to
recommend where to place logs, metrics, and traces.

Run in scratch mode and present the findings report **inline** — do not write any files. For each
instrumentation gap, cite the `path:line`, name the signal type (structured log, counter,
histogram, or span), and state the debugging question it would answer.

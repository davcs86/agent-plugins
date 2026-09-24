---
name: feature-gap-scan
description: feature-gap maps the surface and flags the missing delete + undocumented command, cited, read-only
tags: [smoke, feature-gap]
plugins: ["../.."]
runs: 2
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill, Task]
expected_outcome: An inline surface report citing src/routes.js, flagging the missing delete (feature gap) and/or the undocumented purge command (low discoverability), marked recommendation-only; no files written.
---

This repository exposes a user-facing surface under `src/`. Use the repo-surveyor **feature-gap**
skill to analyze it.

Run in scratch mode and present the findings report **inline** — do not write any files. Map the
surface (routes and CLI commands), then report feature gaps, inconsistencies, low-discoverability
features, and any product metrics worth tracking, each tied to a cited `path:line`.

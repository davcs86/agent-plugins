# constitution-forge — library-docs cross-reference (optional)

Load this only when Phase 1 is classifying a **third-party-library usage** finding **and** a
documentation-lookup MCP tool is available in the host session. It is an *enhancement* to the
inclusion test, never a requirement — if no such tool is present, skip it entirely and judge the
finding from code consistency alone (say so, don't block).

## Why

The constitution should hold what an agent would **miss on a normal read**. For library usage, the
sharpest version of that test is: *does the repo deviate from what the library's own docs
recommend?*

- **Deviation** — a custom timeout, a non-default option, a retry/backoff the library doesn't default
  to, an initialization order the docs warn against, a pinned-for-a-reason version. **Keep it** — a
  deliberate departure is exactly the tribal knowledge worth a rule, and its *why* is often a scar.
- **Matches the documented default** — the repo just uses the library the way the docs show. **Drop
  it or demote to a `## Pointers` line** — an agent can look this up for free, so it fails the litmus.

This turns "is this pattern interesting?" from a guess into a doc-grounded decision, and keeps the
file from filling up with library-idiomatic noise.

## How (with Context7, the reference tool)

1. **Resolve the library.** Call the docs tool's resolver (Context7: `resolve-library-id`) with the
   dependency name taken from the repo's manifest (`package.json`, `go.mod`, `pyproject.toml`, …) —
   never a guessed name (**CF-1**). No match → treat as "no docs available" and fall back.
2. **Query the specific surface.** Ask about the exact API/option the finding is about (Context7:
   `query-docs`), scoped to the resolved library — e.g. "default HTTP client timeout", "connection
   pool defaults", "recommended retry configuration".
3. **Classify** the finding as *deviation* or *default* per the rule above, and record the basis:
   - a deviation becomes a rule/norm whose **Why** cites both the code sites and "deviates from
     `<library>` documented default (`<what the docs say>`)";
   - a default becomes a pointer or is dropped.
4. **Version awareness.** Pin the query to the version the repo actually uses (from the lockfile) when
   the tool supports it; a "deviation" against the wrong major version is a false positive.

## Guardrails

- **Optional and non-blocking.** Missing tool, unresolved library, or a failed query → fall back to
  consistency-based judgment. Never make the constitution depend on an external service being up.
- **Evidence discipline still applies (CF-1).** What you learned from docs is evidence *for
  classification*; the rule itself is still grounded in the repo's own code sites. Cite the docs as
  the reason a usage counts as a deviation, not as the rule's primary evidence.
- **Cost control.** Only consult docs for findings that survived the first inclusion cut and are
  genuinely library-specific. Don't look up every import; look up the handful where deviation-vs-
  default actually changes the keep/drop decision.

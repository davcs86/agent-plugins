# constitution-forge — library-docs cross-reference (optional)

Load this only when Phase 1 is classifying a **third-party-library usage** finding **and** a
documentation-lookup MCP tool is available in the host session. It is an *enhancement* to the
inclusion test, never a requirement — if no such tool is present, skip it entirely and judge the
finding from code consistency alone (say so, don't block).

## Detecting a docs tool (vendor-neutral, both name forms)

This is not tied to one provider. Any MCP tool that resolves a library and returns its documentation
works — Context7 is the reference example, but treat it as *a* docs tool, not *the* docs tool. Look
for a resolve-then-query pair among the session's available tools under any of these shapes:

- **User- or project-configured** server → tools named `mcp__<server>__<tool>`, e.g.
  `mcp__Context7__resolve-library-id` + `mcp__Context7__query-docs`.
- **Plugin-bundled** server (if a host bundles one) → tools named
  `mcp__plugin_<plugin>_<server>__<tool>`, e.g. `mcp__plugin_constitution-forge_Context7__query-docs`.
- **Any equivalent** — a differently-named docs/registry MCP with a resolve + query capability.

Match on capability (resolve a package name → fetch its docs), not on an exact server name. Found one
→ use it as below. Found none, or every call errors → fall back to consistency-based judgment and note
in the run that library-doc classification was unavailable. Never hard-code a single tool name as a
precondition.

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

## How (using the detected tool — Context7 method names shown as the example)

1. **Resolve the library.** Call the tool's resolver (Context7: `resolve-library-id`) with the
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

# feature-gap — surface protocol

Loaded at the start of Phase 0. You are the orchestrator; you dispatch the read-only
`surface-mapper` and then **confirm every lead yourself** before it becomes a finding.

## Step 1 — Delimit the surface

From boot (B1) you have the surface roots — from `userFacingGlobs`, from auto-discovery, or from the
one clarifying question. Decide clustering by **surface kind**, because each kind has its own
contract to read:

- **UI** routes/views · **MCP** tool/prompt/resource defs · **CLI** commands/flags · **public API**
  (OpenAPI/GraphQL/exported symbols/HTTP handlers).
- Small repo → one `surface-mapper`. Large/multi-surface repo → one mapper **per kind or per
  module, in parallel** (one message, multiple Task calls), each returning a scoped inventory.

## Step 2 — Dispatch `surface-mapper`

Hand each mapper its surface kind and roots. It returns, for that surface: a structured inventory
(each element with its **contract** — the route + method, the tool name + input schema, the command
+ flags, the API symbol + signature — and its **adjacent doc/help**, or "none found"), plus flagged
leads in three buckets: gaps, inconsistencies, discoverability. It never writes and never pastes
whole files.

## Step 3 — Confirm every lead (the orchestrator — RS-1, RS-3)

A mapper's flag is a **lead**. Promote it only after you check it:

- **Feature gap** — before asserting a capability is missing, **grep for it** (a differently named
  handler, a flag, a route) so you do not report a gap that is merely elsewhere. Confirm the gap is
  real and that a user would reasonably expect it (an implied-by-siblings CRUD hole, a missing
  recovery/undo/pagination). A gap you cannot ground → `needs-confirmation`.
- **Inconsistency** — open **all** the sibling elements and confirm they truly diverge where they
  should match (naming/arg-shape/error-contract/defaults/casing), and that one side is not already
  handling the case. Cite each side.
- **Low discoverability** — confirm the feature **works** (it is wired, not dead) **and** that it
  has no doc/help/description/trigger surface. A feature with a doc is discoverable, not hidden; a
  "feature" that is actually dead code is a `debt-radar` matter — cross-reference it (**RS-N5**).

## Step 4 — Reason as a PM, ground as an engineer

For each confirmed finding, add the product judgment — always tied to the cited surface:

- **Severity** — the `severity-rubric.md` level and the trigger it meets. A broken/misleading
  contract across sibling surfaces is high; a cosmetic naming drift in a quiet corner is low.
- **Recommended features** — additive ideas the surface motivates, each with a rationale and a
  **trade-off both ways** (**RS-N3**): what building it buys vs. its cost/complexity/maintenance.
- **Product metrics** — for each key feature, name *what* to measure and *why* it tells you the
  feature works for users: adoption (is it used), activation (do new users reach it), funnel
  drop-off (where do they abandon), task success/error rate. State the **read point** (which
  event/surface the metric is read from). Where the metric needs a new counter/event in code, add a
  **→ signal-map** cross-reference for the *placement* — that is `signal-map`'s side of the seam
  (**RS-N5, RS-N4**). Never attach a value — you have not measured it.

## Step 5 — Compose

Order findings by leverage within each severity band (**RS-N2**); keep to the ones that earn their
place (**RS-N8**). Record the survey's branch+commit (`git rev-parse`) and the explicit
**"static, recommendation-only — no live metrics observed"** note (**RS-N4**) for the header. Return
to Phase 1 to render the template and gate the write.

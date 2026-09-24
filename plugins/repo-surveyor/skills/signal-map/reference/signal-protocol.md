# signal-map — signal protocol

Loaded at the start of Phase 0. You are the orchestrator; you dispatch the read-only
`instrumentation-scout` and then **confirm every lead yourself** before it becomes a finding.

## Step 1 — Frame the survey

From boot (B1) you know the analysis root and the **existing** observability stack (logging lib,
metrics/OTel/StatsD/Prometheus client, tracing). Every recommendation must use that stack
(**RS-N7**); if there is none, note that introducing one is part of the LOE. Decide clustering:

- Small service → one `instrumentation-scout`.
- Large repo / multiple services → one scout **per service or module, in parallel** (one message,
  multiple Task calls), each returning a scoped signal map.

## Step 2 — Dispatch `instrumentation-scout`

Hand each scout its scope and the detected observability stack. It returns a map of the
**diagnostically interesting points** — error/exception branches, retries/fallbacks, hot paths
(loops, request handlers, batch jobs), external/IO calls (network, DB, queue, filesystem), and
feature-boundary crossings — each annotated with the **existing** signal there (log/metric/span) or
"none", plus flagged gaps, noisy/redundant signals, and cardinality hazards. It never writes.

## Step 3 — Confirm every lead (the orchestrator — RS-1, RS-3)

A scout's flag is a **lead**. Promote it only after you check it:

- **Instrumentation gap** — open the cited branch/path and confirm (a) there is genuinely no signal
  and (b) the point is genuinely load-bearing: an error path that would page someone, a hot path
  whose latency matters, an external call that fails in production. A trivial path where a signal
  would be pure noise is **not** a gap — surgical means leaving those alone.
- **Redundant / noisy** — confirm the log/metric truly duplicates another or sits in a tight loop /
  hot path where it floods. Removing signal is a real recommendation; ground it like any other.
- **Cardinality hazard** — confirm the label/dimension is genuinely unbounded (user-id, request-id,
  full URL as a metric tag). Cite the site.

Anything you cannot ground → `needs-confirmation` (**RS-N6**).

## Step 4 — Specify each signal surgically

For every confirmed finding, specify it precisely — a recommendation an engineer could act on
without guessing:

- **Signal type** — structured log (with the fields that make it useful), counter, histogram/timer,
  span, or event. Choose the *cheapest type that answers the question*: a counter over a log where a
  count suffices; a histogram where you need percentiles; a span where you need causal timing across
  calls.
- **The question it answers** — the concrete debugging or performance question the signal makes
  answerable ("why did this request 500?", "what is the p95 of this handler?", "how often does the
  fallback fire?"). A signal with no question behind it is noise (**RS-N4**: it is a *recommendation
  to measure*, never a claimed value).
- **Severity** — the `severity-rubric.md` level and its trigger. No signal over a paging error class
  is high; a nice-to-have gauge on a quiet path is low.
- **Trade-off both ways (RS-N3)** — the **blind spot** the missing signal leaves vs. the **cost** of
  the signal (runtime overhead, storage/ingest cost, cardinality). For a removal: the noise/cost cut
  vs. what visibility is lost.

## Step 5 — Respect the seam and compose

- **Feature-performance gauges** cross-reference the `feature-gap` feature they measure (**RS-N5**);
  you specify the *placement*, `feature-gap` owns the *what/why*.
- Order findings by leverage within each severity band (**RS-N2**); keep to what earns its place —
  a surgical plan is short (**RS-N8**). Record branch+commit (`git rev-parse`), the existing stack,
  and the **"static, recommendation-only"** note (**RS-N4**) for the header. Return to Phase 1 to
  render the template and gate the write.

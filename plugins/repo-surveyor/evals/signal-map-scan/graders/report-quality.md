---
type: llm
focus: last_message
weight: 2
---

PASS if the reply is an instrumentation report that:
- cites the `path:line` of the silent failure branch in `src/fetcher.py` (the `except
  requests.RequestException` that returns `None` with no log/metric/trace);
- names a concrete **signal type** to add there (structured log, counter, histogram/timer, or
  span);
- states the **debugging or performance question** the signal would answer; and
- assigns a **severity**, and frames it as a recommendation (no observed latency/error-rate value).

FAIL if it reports an observed metric value as if measured, edits code, or cites nothing.

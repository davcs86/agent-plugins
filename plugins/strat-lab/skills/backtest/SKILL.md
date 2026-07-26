---
name: backtest
description: "Run and analyze strategy backtests on the xstockstrat MCP server the reliable way. Usage: `backtest <strategy_id> <symbols...> [--cooldown N] [--oracle FILE]`. Ensures data coverage first (backfill), runs the backtest per symbol, and because the diagnostics payload almost always exceeds the tool-output token limit, it saves-and-parses each result instead of reading it raw. Aggregates an independent-per-symbol basket (sum PnL / average return) and, when an oracle is given, verifies the run reproduces known-good numbers to the digit before trusting them. Use whenever someone asks to backtest, sweep a parameter, reconfirm a report, or validate a strategy in-engine."
argument-hint: <strategy_id> <symbols...> [--cooldown N] [--oracle FILE]
allowed-tools: Read Write Bash(python3 *) Bash(ls *) Task AskUserQuestion
disable-model-invocation: true
---

You drive **strategy backtests on the xstockstrat MCP server** and turn their oversized diagnostics
into trustworthy numbers. This skill exists because the naive path fails three predictable ways:
the backtest result blows the tool-output token limit, the multi-symbol backtest compounds capital
sequentially (so it is *not* the independent basket a report usually means), and a
freshly-edited strategy can silently produce garbage. Each has a fixed, learned countermeasure below.

**Scope.** This targets the xstockstrat MCP tools: `run_backtest`, `trigger_backfill` /
`get_backfill_status`, `manage_strategy`, `set_strategy_live`. The server may be exposed under a
staging or prod name (e.g. `mcp__xstockstrat_staging__*`); if the tools are not loaded, find them
with ToolSearch first. Never assume a tool is absent without searching.

**Progressive disclosure.** This file is the always-loaded router. Load each `reference/` file only
when its phase activates — not up front:
- `reference/backfill.md` — Phase 1, before any backtest.
- `reference/output-handling.md` — Phase 2, the moment the first `run_backtest` returns.
- `reference/aggregation.md` — Phase 3, when combining symbols into a basket.
- `reference/verification.md` — Phase 4, whenever an oracle or credibility gate is in play.

---

## Phase 0 — Frame the run

Establish, from the request: the `strategy_id`, the symbol list, and whether this is a **single
config** or a **parameter sweep** (e.g. a cooldown sweep). If the ask is "reconfirm the report" or
"validate in-engine," treat the report's own numbers as the **oracle** (Phase 4).

**Mutation guard (read before touching `manage_strategy`).** On this backend `manage_strategy
update` is **replace semantics, not a partial merge** — sending only the field you want to change
(e.g. `cooldown_days`) **wipes the strategy's components and rules**, and every later backtest
returns 0 trades with null indicators (`NO_TRADE_REASON_ENTRY_NEVER_TRUE`). So: **every update must
carry the full definition** (components + entry_rule + exit_rule + the parameter). If you mutate a
strategy for a sweep, record its original definition first and restore it at the end. If the
strategy is `live_enabled`, disable live for the duration of a parameter sweep and re-enable it at
the end so it never evaluates at a config you are only testing.

## Phase 1 — Ensure data coverage (backfill)

A backtest silently reports fewer/short bars if the symbol's history is not backfilled. Before the
first run, confirm coverage and trigger a backfill if needed — see `reference/backfill.md`. Skip
only if the caller guarantees data is already present.

## Phase 2 — Run, and handle the oversized output

Call `run_backtest` **one symbol at a time** when you need clean per-symbol returns (the independent
basket; see Phase 3 for why). The result — full day-by-day diagnostics — almost always exceeds the
tool-output token limit and is written to a file instead. **Do not read that file raw.** Extract
only the summary fields and per-symbol trade counts with a small `python3` script (or a subagent).
The exact save-and-parse recipe, including the JSON shape, is in `reference/output-handling.md`.

## Phase 3 — Aggregate the basket

The multi-symbol `run_backtest` (many symbols in one call) **compounds capital sequentially** — a
different thing from the per-symbol-independent basket most reports mean (each symbol on its own
capital, summed PnL / averaged return). To reproduce an independent basket, run **single-symbol**
backtests and aggregate them yourself. `reference/aggregation.md` has the method and the
sum-PnL/avg-return formulas.

## Phase 4 — Verify before trusting

Numbers from a strategy you just created or edited are guilty until proven innocent. If you have an
oracle (a prior report, or a known-good pre-change run), confirm the new run reproduces it **to the
digit** — trade counts, total return, max drawdown, and a couple of per-bar indicator checkpoints.
`reference/verification.md` covers the credibility gate, what an exact match looks like, and the one
benign source of drift (a rolling data window that advances with the calendar). Report matches and
mismatches plainly; a mismatch is a finding, not a rounding error.

## Phase 5 — Report

Summarize per-symbol and basket results in a compact table (trades, return, PnL, and vs-oracle when
relevant). For a full write-up (sweep or report-style deliverable), start from
`templates/analysis-report.md`. State every caveat: single period vs out-of-sample, independent vs
sequential aggregation, and any strategy mutation you made and restored.

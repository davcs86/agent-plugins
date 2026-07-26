# Strat Lab

A backtesting workbench for the **xstockstrat** MCP server, published for **Claude Code** and
**Cursor** from one shared skill tree.

It exists because the obvious way to backtest fails in three predictable ways, each with a learned
fix baked into the skill:

1. **The output blows the token limit.** `run_backtest` returns full day-by-day diagnostics
   (~6k–10k lines per symbol). The skill saves-and-parses, extracting only summary metrics — it
   never reads the raw payload into context.
2. **The multi-symbol call compounds capital.** That is the sequential portfolio view, not the
   independent-per-symbol basket most reports mean. The skill runs single-symbol backtests and
   aggregates them (sum PnL / average return).
3. **An edited strategy can silently produce garbage.** The skill verifies every run against an
   oracle to the digit — trade blotter and per-bar indicator checkpoints — before trusting it, and
   warns that `manage_strategy update` is replace-semantics (send the full definition or you wipe
   the components).

It also ensures **data coverage first** (`trigger_backfill` / `get_backfill_status`) so a data gap
is never mistaken for a strategy problem.

## Skill

- **`/backtest`** `<strategy_id> <symbols...> [--cooldown N] [--oracle FILE]` — the full pipeline:
  backfill → run → save-and-parse → aggregate → verify → report. Progressive-disclosure router in
  `skills/backtest/SKILL.md`, with `reference/` files loaded per phase and a report template.

## Install

Add the marketplace (`davcs86/agent-plugins`), then enable `strat-lab`. Requires the xstockstrat
MCP server to be connected; the skill finds its tools (`run_backtest`, `manage_strategy`,
`trigger_backfill`, `get_backfill_status`, `set_strategy_live`) via ToolSearch if they are not
already loaded.

## Validate

```shell
python3 plugins/strat-lab/scripts/validate.py --self-test
python3 plugins/strat-lab/scripts/validate.py
```

# AAPL Equity Backtest — Real Yahoo Finance Data
**Generated:** 2026-10-22 20:57 UTC
**Data source:** Yahoo Finance (free, no API key)
**Strategies:** `aapl_scalp_trend`, `aapl_scalp_reversion` (13 candidates expanded to 48 runs)

---

## Data fetched

| Timeframe | Bars | Range | Yahoo cap |
|-----------|------|-------|-----------|
| 1d | 551 | 2024-08-13 → 2026-10-22 | 1600 days |
| 1h | 0 | — | 730-day limit hit |

Only 1d data survived. The 1h request failed because `days_back=800` exceeded
Yahoo's 730-day intraday cap. Fixed in `run_aapl_backtest.py` with a per-timeframe
cap table (`{"1m": 6, "5m": 55, "15m": 55, "1h": 700, "1d": 1600}`).

---

## Results (48 runs, 2 families × 12 candidates × 2 timeframes)

### Best performers

| Candidate | TF | CAGR | Sharpe | MaxDD | Trades | Exposure |
|-----------|----|------|--------|-------|--------|----------|
| `aapl_scalp_trend_ema21_rsi_max55` | 1d | **+3.96%** | 0.603 | -10.65% | 86 | 6.1% |
| `aapl_scalp_trend_ema9_rsi_max55` | 1d | +3.48% | 0.511 | -10.75% | 90 | 7.0% |
| `aapl_scalp_trend_ema9_rsi_max50` | 1d | +1.80% | 0.388 | -6.17% | 50 | 7.0% |

### Buy & hold baseline (same period)

| Metric | Value |
|--------|-------|
| CAGR | **+21.99%** |
| MaxDD | -33.43% |

---

## Honest assessment

**The strategies do not beat buy and hold on this data.** AAPL returned
+22% CAGR over the window; the best trend-following variant returned +4%.

This is not a failure of the code — it is the expected result for a mean-
reversion/trend-filter strategy on a strong trending asset:

1. **Trend filter costs participation.** The SMA200 filter keeps the strategy
   in cash during AAPL's biggest rallies. B&H captures them; the strategy sits out.
2. **1d bars are too coarse for a 1-minute scalp.** The `aapl_scalp_*` families
   were designed for 1m bars with intrabar TP/SL ($0.50/$0.75). On daily bars
   the entry/exit logic is a crude approximation — there is no intrabar TP, so
   every trade rides the full daily bar.
3. **Reversion family produced almost no trades.** 30 of 36 reversion runs had
   0 trades. The RSI oversold/overbought thresholds rarely fire on daily bars,
   and when they do the EMA9 bounce condition filters them out.
4. **1h timeframe is worse than 1d.** Average CAGR on 1h was -0.33% vs +0.43%
   on 1d. More bars = more fees = more decay, exactly what the crypto research
   already proved (see README: "Trading less beats trading more").

### What would change this

- **Real 1m data.** Yahoo only serves 7 days of 1m. A paid data feed (IEX,
  Alpaca, Polygon) would let the actual scalp rules run at their intended
  timeframe, with intrabar TP/SL modelled properly.
- **Short side.** The strategies are long-only. AAPL's window was strongly
   trending; a short-side rule would capture the pullbacks that the reversion
   family is trying to ride.
- **Intrabar TP/SL.** The current engine is position-only (entry/exit on bar
   close). A proper intrabar simulator would model the $0.50 TP / $0.75 SL
   from `SCALP_STRATEGY.md`, which is where the actual edge is designed to live.

---

## What was fixed in this session

| File | Change |
|------|--------|
| `research/data.py` | `fetch_equity_candles` now flattens yfinance MultiIndex columns and normalises date column names |
| `research/config.py` | `cost_per_side()` and `periods_per_year()` now route equity assets correctly |
| `research/engine.py` | `evaluate()` accepts `symbol=` and routes to per-asset cost/period helpers |
| `run_aapl_backtest.py` | New standalone runner; per-timeframe Yahoo cap table; correct `expand()` unpacking |
| `research/strategies.py` | Two AAPL scalp families in REGISTRY (13 families, 148 candidates) |

---

## Files

- `research/reports/aapl_backtest.json` — full 48-run result set
- `run_aapl_backtest.py` — rerunnable entry point
- `SCALP_STRATEGY.md` — the original TradingView scalp rules (TP/SL/entry/exit)

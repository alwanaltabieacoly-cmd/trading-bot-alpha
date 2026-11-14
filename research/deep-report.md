# Deep research report

- Runs analysed: **102**
- Candidates per run: ~142
- Cumulative candidates evaluated: **14,160**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-14 23:13:08+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3986** (min 0.1793, max 0.612, over 102 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.7% | -17.0% | 0.166 | 0.226 | 1122 | 0 |
| `sma_trend_vol_filter` | 15.5% | 15.0% | -10.2% | 0.150 | 0.607 | 3379 | 0 |
| `sma_trend_efficiency` | 12.3% | 13.0% | -14.1% | 0.274 | 0.493 | 1540 | 0 |
| `ema_trend` | 10.7% | 11.2% | -16.2% | 0.114 | 0.155 | 589 | 0 |
| `ema_trend_regime` | 9.7% | 9.5% | -11.3% | 0.075 | 0.243 | 897 | 0 |
| `sma_trend_fast_slow` | 7.2% | 8.1% | -16.4% | 0.140 | 0.229 | 1063 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.1% | 0.112 | 0.184 | 1092 | 0 |
| `sma_trend_confirm` | 6.9% | 5.3% | -17.1% | 0.101 | 0.179 | 666 | 0 |
| `donchian_trend` | 3.3% | 2.3% | -4.0% | 0.299 | 0.429 | 246 | 0 |
| `donchian_trend_vol_filter` | 2.1% | 1.7% | -2.8% | 0.073 | 0.311 | 218 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 102 | 102 | 30.4% | 24.7% | 0.468 | 8.8 |
| `sma_trend_period200` | 102 | 102 | 28.5% | 20.5% | 0.167 | 9.4 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 102 | 102 | 28.1% | 21.2% | 0.483 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 102 | 102 | 28.1% | 22.9% | 0.207 | 9.8 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 102 | 102 | 25.9% | 19.6% | 0.479 | 8.8 |
| `sma_trend_period175` | 102 | 102 | 25.7% | 16.9% | 0.130 | 9.2 |
| `sma_trend_period50` | 102 | 102 | 25.7% | 13.2% | 0.202 | 8.7 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 102 | 102 | 24.9% | 17.2% | 0.469 | 9.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 102 | 102 | 23.9% | 18.1% | 0.122 | 8.8 |
| `sma_trend_period225` | 102 | 102 | 23.8% | 16.2% | 0.164 | 9.1 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 89 | 6.6% | -3.6% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 50 | 5.0% | -2.5% |
| `sma_trend_slope_period150_slope_bars40` | 47 | 12.3% | -3.5% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 102/102 runs (mean holdout 30.4%, worst 24.7%, mean DSR 0.468)
- KEEP: `sma_trend_period200` was positive in 102/102 runs (mean holdout 28.5%, worst 20.5%, mean DSR 0.167)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 102/102 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.483)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 102/102 runs (mean holdout 28.1%, worst 22.9%, mean DSR 0.207)
- KEEP: `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` was positive in 102/102 runs (mean holdout 25.9%, worst 19.6%, mean DSR 0.479)
- FAMILY `sma_trend` has the best median holdout CAGR (19.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.0%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.2%) - add more parameters to it


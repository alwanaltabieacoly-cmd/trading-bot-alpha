# Deep research report

- Runs analysed: **74**
- Candidates per run: ~142
- Cumulative candidates evaluated: **10,184**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-07 00:11:48+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4392** (min 0.1793, max 0.612, over 74 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.1% | 21.0% | -16.8% | 0.163 | 0.213 | 814 | 0 |
| `sma_trend_vol_filter` | 16.2% | 15.5% | -10.4% | 0.144 | 0.600 | 2453 | 0 |
| `ema_trend` | 12.3% | 13.0% | -15.8% | 0.113 | 0.155 | 441 | 0 |
| `sma_trend_efficiency` | 12.6% | 12.9% | -14.0% | 0.269 | 0.488 | 1092 | 0 |
| `ema_trend_regime` | 10.4% | 10.5% | -11.3% | 0.071 | 0.231 | 643 | 0 |
| `sma_trend_slope` | 8.9% | 9.7% | -14.9% | 0.110 | 0.183 | 811 | 0 |
| `sma_trend_fast_slow` | 8.2% | 9.2% | -16.3% | 0.136 | 0.226 | 803 | 0 |
| `sma_trend_confirm` | 8.0% | 6.3% | -17.0% | 0.100 | 0.178 | 499 | 0 |
| `donchian_trend` | 2.7% | 2.0% | -4.1% | 0.300 | 0.429 | 162 | 0 |
| `donchian_trend_vol_filter` | 1.6% | 1.2% | -2.9% | 0.076 | 0.311 | 159 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 74 | 74 | 31.5% | 24.9% | 0.455 | 8.8 |
| `sma_trend_period200` | 74 | 74 | 30.6% | 21.8% | 0.164 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 74 | 74 | 29.6% | 21.4% | 0.472 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 74 | 74 | 29.0% | 23.1% | 0.192 | 9.8 |
| `sma_trend_period175` | 74 | 74 | 28.2% | 17.7% | 0.127 | 9.4 |
| `sma_trend_period50` | 74 | 74 | 27.9% | 13.2% | 0.196 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 74 | 74 | 27.0% | 19.7% | 0.467 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 74 | 74 | 26.5% | 17.4% | 0.448 | 10.3 |
| `sma_trend_period225` | 74 | 74 | 25.9% | 16.5% | 0.160 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 74 | 74 | 24.8% | 18.2% | 0.111 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 61 | 6.6% | -3.1% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 33 | 9.9% | -0.9% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 22 | 5.0% | -2.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 21 | 9.9% | -0.8% |
| `sma_trend_slope_period100_slope_bars10` | 20 | 13.1% | -1.2% |
| `sma_trend_slope_period150_slope_bars40` | 19 | 12.7% | -3.0% |
| `sma_trend_confirm_slow_period150_fast_period50` | 14 | 12.5% | -0.7% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `ema_trend_fast50_slow300` | 3 | 8.0% | -1.7% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 74/74 runs (mean holdout 31.5%, worst 24.9%, mean DSR 0.455)
- KEEP: `sma_trend_period200` was positive in 74/74 runs (mean holdout 30.6%, worst 21.8%, mean DSR 0.164)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 74/74 runs (mean holdout 29.6%, worst 21.4%, mean DSR 0.472)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 74/74 runs (mean holdout 29.0%, worst 23.1%, mean DSR 0.192)
- KEEP: `sma_trend_period175` was positive in 74/74 runs (mean holdout 28.2%, worst 17.7%, mean DSR 0.127)
- FAMILY `sma_trend` has the best median holdout CAGR (21.0%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.5%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.9%) - add more parameters to it


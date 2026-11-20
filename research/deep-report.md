# Deep research report

- Runs analysed: **119**
- Candidates per run: ~142
- Cumulative candidates evaluated: **16,574**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-20 03:36:01+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3879** (min 0.1793, max 0.612, over 119 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.5% | -17.1% | 0.167 | 0.226 | 1309 | 0 |
| `sma_trend_vol_filter` | 15.9% | 15.6% | -10.1% | 0.152 | 0.607 | 3913 | 0 |
| `sma_trend_efficiency` | 12.4% | 13.3% | -14.2% | 0.276 | 0.499 | 1812 | 0 |
| `ema_trend` | 10.4% | 10.6% | -16.4% | 0.115 | 0.155 | 691 | 0 |
| `ema_trend_regime` | 9.9% | 9.8% | -11.2% | 0.076 | 0.243 | 1033 | 0 |
| `sma_trend_fast_slow` | 7.3% | 8.1% | -16.4% | 0.141 | 0.233 | 1233 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.2% | 0.113 | 0.186 | 1279 | 0 |
| `sma_trend_confirm` | 7.0% | 5.5% | -17.0% | 0.102 | 0.181 | 802 | 0 |
| `donchian_trend` | 3.6% | 2.5% | -3.9% | 0.298 | 0.429 | 297 | 0 |
| `donchian_trend_vol_filter` | 2.4% | 2.3% | -2.7% | 0.072 | 0.311 | 252 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 119 | 119 | 30.6% | 24.7% | 0.474 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 119 | 119 | 28.5% | 22.9% | 0.213 | 9.8 |
| `sma_trend_period200` | 119 | 119 | 28.2% | 20.5% | 0.169 | 9.4 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 119 | 119 | 28.1% | 21.2% | 0.487 | 9.1 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 119 | 119 | 26.0% | 19.6% | 0.485 | 8.6 |
| `sma_trend_period50` | 119 | 119 | 25.9% | 13.2% | 0.201 | 8.7 |
| `sma_trend_period175` | 119 | 119 | 25.2% | 16.9% | 0.131 | 9.4 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 119 | 119 | 25.0% | 17.2% | 0.472 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 119 | 119 | 24.2% | 18.1% | 0.127 | 8.7 |
| `sma_trend_period225` | 119 | 119 | 23.5% | 16.2% | 0.165 | 8.8 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 106 | 6.5% | -3.5% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 67 | 5.0% | -2.1% |
| `sma_trend_slope_period150_slope_bars40` | 64 | 12.1% | -2.9% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 119/119 runs (mean holdout 30.6%, worst 24.7%, mean DSR 0.474)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 119/119 runs (mean holdout 28.5%, worst 22.9%, mean DSR 0.213)
- KEEP: `sma_trend_period200` was positive in 119/119 runs (mean holdout 28.2%, worst 20.5%, mean DSR 0.169)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 119/119 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.487)
- KEEP: `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` was positive in 119/119 runs (mean holdout 26.0%, worst 19.6%, mean DSR 0.485)
- FAMILY `sma_trend` has the best median holdout CAGR (19.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.6%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (10.6%) - add more parameters to it


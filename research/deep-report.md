# Deep research report

- Runs analysed: **92**
- Candidates per run: ~142
- Cumulative candidates evaluated: **12,740**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-12 03:56:08+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4063** (min 0.1793, max 0.612, over 92 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.4% | 20.1% | -17.0% | 0.165 | 0.226 | 1012 | 0 |
| `sma_trend_vol_filter` | 15.4% | 14.8% | -10.3% | 0.148 | 0.607 | 3047 | 0 |
| `sma_trend_efficiency` | 12.3% | 12.8% | -14.1% | 0.273 | 0.491 | 1380 | 0 |
| `ema_trend` | 11.0% | 11.6% | -16.1% | 0.114 | 0.155 | 531 | 0 |
| `ema_trend_regime` | 9.6% | 9.5% | -11.3% | 0.073 | 0.243 | 807 | 0 |
| `sma_trend_fast_slow` | 7.2% | 8.2% | -16.4% | 0.139 | 0.228 | 963 | 0 |
| `sma_trend_slope` | 7.7% | 7.5% | -15.1% | 0.111 | 0.184 | 982 | 0 |
| `sma_trend_confirm` | 6.9% | 5.3% | -17.1% | 0.101 | 0.179 | 588 | 0 |
| `donchian_trend` | 3.1% | 2.1% | -4.0% | 0.299 | 0.429 | 216 | 0 |
| `donchian_trend_vol_filter` | 1.9% | 1.3% | -2.8% | 0.074 | 0.311 | 198 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 92 | 92 | 30.4% | 24.7% | 0.464 | 8.8 |
| `sma_trend_period200` | 92 | 92 | 28.9% | 20.5% | 0.166 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 92 | 92 | 28.3% | 21.2% | 0.480 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 92 | 92 | 28.1% | 22.9% | 0.202 | 9.8 |
| `sma_trend_period175` | 92 | 92 | 26.3% | 16.9% | 0.129 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 92 | 92 | 25.9% | 19.6% | 0.475 | 8.8 |
| `sma_trend_period50` | 92 | 92 | 25.8% | 13.2% | 0.201 | 8.7 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 92 | 92 | 25.0% | 17.2% | 0.463 | 9.8 |
| `sma_trend_period225` | 92 | 92 | 24.2% | 16.2% | 0.162 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 92 | 92 | 23.9% | 18.1% | 0.118 | 8.9 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 79 | 6.6% | -3.7% |
| `sma_trend_confirm_slow_period100_fast_period50` | 51 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 40 | 5.1% | -2.9% |
| `sma_trend_slope_period150_slope_bars40` | 37 | 12.4% | -3.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 21 | 8.2% | -2.5% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 92/92 runs (mean holdout 30.4%, worst 24.7%, mean DSR 0.464)
- KEEP: `sma_trend_period200` was positive in 92/92 runs (mean holdout 28.9%, worst 20.5%, mean DSR 0.166)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 92/92 runs (mean holdout 28.3%, worst 21.2%, mean DSR 0.480)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 92/92 runs (mean holdout 28.1%, worst 22.9%, mean DSR 0.202)
- KEEP: `sma_trend_period175` was positive in 92/92 runs (mean holdout 26.3%, worst 16.9%, mean DSR 0.129)
- FAMILY `sma_trend` has the best median holdout CAGR (20.1%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.8%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.8%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.6%) - add more parameters to it


# Deep research report

- Runs analysed: **90**
- Candidates per run: ~142
- Cumulative candidates evaluated: **12,456**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-11 15:26:08+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4092** (min 0.1793, max 0.612, over 90 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.6% | 20.2% | -17.0% | 0.165 | 0.226 | 990 | 0 |
| `sma_trend_vol_filter` | 15.5% | 14.8% | -10.3% | 0.148 | 0.607 | 2981 | 0 |
| `sma_trend_efficiency` | 12.3% | 12.8% | -14.1% | 0.273 | 0.491 | 1348 | 0 |
| `ema_trend` | 11.1% | 11.6% | -16.0% | 0.114 | 0.155 | 521 | 0 |
| `ema_trend_regime` | 9.6% | 9.5% | -11.3% | 0.073 | 0.241 | 789 | 0 |
| `sma_trend_fast_slow` | 7.3% | 8.2% | -16.4% | 0.139 | 0.228 | 944 | 0 |
| `sma_trend_slope` | 7.8% | 7.9% | -15.1% | 0.111 | 0.184 | 961 | 0 |
| `sma_trend_confirm` | 7.0% | 5.3% | -17.1% | 0.101 | 0.179 | 577 | 0 |
| `donchian_trend` | 3.0% | 2.1% | -4.0% | 0.299 | 0.429 | 210 | 0 |
| `donchian_trend_vol_filter` | 1.9% | 1.3% | -2.8% | 0.074 | 0.311 | 194 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 90 | 90 | 30.5% | 24.7% | 0.463 | 8.8 |
| `sma_trend_period200` | 90 | 90 | 29.0% | 20.7% | 0.166 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 90 | 90 | 28.4% | 21.2% | 0.479 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 90 | 90 | 28.1% | 22.9% | 0.201 | 9.8 |
| `sma_trend_period175` | 90 | 90 | 26.4% | 17.1% | 0.129 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 90 | 90 | 26.0% | 19.6% | 0.475 | 8.8 |
| `sma_trend_period50` | 90 | 90 | 25.9% | 13.2% | 0.200 | 8.7 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 90 | 90 | 25.1% | 17.2% | 0.461 | 9.8 |
| `sma_trend_period225` | 90 | 90 | 24.4% | 16.2% | 0.162 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 90 | 90 | 23.9% | 18.1% | 0.118 | 8.9 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 77 | 6.6% | -3.7% |
| `sma_trend_confirm_slow_period100_fast_period50` | 49 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 38 | 5.1% | -2.9% |
| `sma_trend_slope_period150_slope_bars40` | 35 | 12.4% | -3.6% |
| `sma_trend_confirm_slow_period100_fast_period20` | 33 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 32 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 25 | 11.9% | -0.9% |
| `ema_trend_fast50_slow300` | 19 | 8.2% | -2.5% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 13 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 90/90 runs (mean holdout 30.5%, worst 24.7%, mean DSR 0.463)
- KEEP: `sma_trend_period200` was positive in 90/90 runs (mean holdout 29.0%, worst 20.7%, mean DSR 0.166)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 90/90 runs (mean holdout 28.4%, worst 21.2%, mean DSR 0.479)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 90/90 runs (mean holdout 28.1%, worst 22.9%, mean DSR 0.201)
- KEEP: `sma_trend_period175` was positive in 90/90 runs (mean holdout 26.4%, worst 17.1%, mean DSR 0.129)
- FAMILY `sma_trend` has the best median holdout CAGR (20.2%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.8%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.8%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.6%) - add more parameters to it


# Deep research report

- Runs analysed: **15**
- Candidates per run: ~124
- Cumulative candidates evaluated: **1,788**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-22 20:12:03+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.2449** (min 0.1793, max 0.4476, over 15 runs)
- Verdict: **search is weakly informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 18.8% | 18.1% | -16.5% | 0.142 | 0.202 | 165 | 0 |
| `sma_trend_vol_filter` | 14.2% | 14.1% | -10.5% | 0.111 | 0.503 | 495 | 0 |
| `sma_trend_efficiency` | 13.5% | 12.0% | -13.7% | 0.220 | 0.411 | 180 | 0 |
| `ema_trend` | 10.0% | 11.5% | -15.2% | 0.107 | 0.155 | 90 | 0 |
| `sma_trend_fast_slow` | 5.5% | 8.4% | -16.5% | 0.115 | 0.187 | 150 | 0 |
| `ema_trend_regime` | 7.7% | 8.1% | -11.2% | 0.051 | 0.128 | 113 | 0 |
| `sma_trend_slope` | 6.2% | 7.5% | -14.2% | 0.094 | 0.151 | 120 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.3% | 0.307 | 0.429 | 30 | 0 |
| `sma_trend_confirm` | 5.1% | 1.5% | -16.6% | 0.086 | 0.143 | 68 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.101 | 0.311 | 30 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 15 | 15 | 28.9% | 28.1% | 0.132 | 9.0 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 15 | 15 | 28.2% | 27.4% | 0.350 | 8.0 |
| `sma_trend_period50` | 15 | 15 | 27.3% | 25.9% | 0.187 | 8.0 |
| `sma_trend_period175` | 15 | 15 | 26.5% | 25.7% | 0.104 | 8.0 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 12 | 12 | 26.4% | 26.2% | 0.137 | 9.0 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 15 | 15 | 26.2% | 25.5% | 0.386 | 7.0 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 15 | 15 | 25.8% | 25.0% | 0.089 | 9.0 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 15 | 15 | 25.1% | 24.5% | 0.403 | 10.0 |
| `sma_trend_period225` | 15 | 15 | 23.9% | 23.1% | 0.129 | 9.0 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 15 | 15 | 23.4% | 22.7% | 0.365 | 8.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 15 | 7.1% | -6.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 15 | 4.9% | -2.4% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 12 | 6.7% | -2.2% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max70` | 3 | -1.4% | -9.0% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 15/15 runs (mean holdout 28.9%, worst 28.1%, mean DSR 0.132)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 15/15 runs (mean holdout 28.2%, worst 27.4%, mean DSR 0.350)
- KEEP: `sma_trend_period50` was positive in 15/15 runs (mean holdout 27.3%, worst 25.9%, mean DSR 0.187)
- KEEP: `sma_trend_period175` was positive in 15/15 runs (mean holdout 26.5%, worst 25.7%, mean DSR 0.104)
- KEEP: `sma_trend_efficiency_period200_er_n30_er_min0.2` was positive in 12/12 runs (mean holdout 26.4%, worst 26.2%, mean DSR 0.137)
- FAMILY `sma_trend` has the best median holdout CAGR (18.1%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.0%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.5%) - add more parameters to it


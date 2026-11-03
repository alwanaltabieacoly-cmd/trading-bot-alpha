# Deep research report

- Runs analysed: **62**
- Candidates per run: ~142
- Cumulative candidates evaluated: **8,480**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-03 15:21:22+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.442** (min 0.1793, max 0.612, over 62 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.7% | 21.7% | -16.7% | 0.161 | 0.204 | 682 | 0 |
| `sma_trend_vol_filter` | 16.4% | 15.7% | -10.4% | 0.141 | 0.591 | 2054 | 0 |
| `ema_trend` | 12.8% | 13.6% | -15.7% | 0.112 | 0.155 | 372 | 0 |
| `sma_trend_efficiency` | 12.8% | 12.8% | -14.0% | 0.266 | 0.480 | 900 | 0 |
| `ema_trend_regime` | 10.6% | 10.7% | -11.3% | 0.068 | 0.219 | 536 | 0 |
| `sma_trend_slope` | 9.2% | 9.9% | -14.7% | 0.109 | 0.180 | 677 | 0 |
| `sma_trend_fast_slow` | 8.6% | 9.8% | -16.3% | 0.135 | 0.223 | 676 | 0 |
| `sma_trend_confirm` | 8.4% | 6.4% | -16.8% | 0.099 | 0.175 | 422 | 0 |
| `donchian_trend` | 2.5% | 2.0% | -4.1% | 0.300 | 0.429 | 126 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 1.1% | -3.0% | 0.077 | 0.311 | 134 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 62 | 62 | 31.8% | 27.4% | 0.448 | 8.8 |
| `sma_trend_period200` | 62 | 62 | 31.2% | 25.7% | 0.162 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 62 | 62 | 29.8% | 25.5% | 0.465 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 62 | 62 | 29.2% | 25.0% | 0.183 | 9.8 |
| `sma_trend_period50` | 62 | 62 | 28.9% | 22.9% | 0.194 | 8.9 |
| `sma_trend_period175` | 62 | 62 | 28.8% | 23.8% | 0.125 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 62 | 62 | 27.4% | 22.7% | 0.459 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 62 | 62 | 26.8% | 23.7% | 0.441 | 10.4 |
| `sma_trend_period225` | 62 | 62 | 26.6% | 21.0% | 0.158 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 62 | 62 | 25.2% | 20.7% | 0.105 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 49 | 6.6% | -3.1% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 21 | 9.9% | -0.5% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_confirm_slow_period100_fast_period20` | 17 | 10.0% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 17 | 13.2% | -1.2% |
| `sma_trend_slope_period150_slope_bars40` | 14 | 13.0% | -3.2% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 62/62 runs (mean holdout 31.8%, worst 27.4%, mean DSR 0.448)
- KEEP: `sma_trend_period200` was positive in 62/62 runs (mean holdout 31.2%, worst 25.7%, mean DSR 0.162)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 62/62 runs (mean holdout 29.8%, worst 25.5%, mean DSR 0.465)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 62/62 runs (mean holdout 29.2%, worst 25.0%, mean DSR 0.183)
- KEEP: `sma_trend_period50` was positive in 62/62 runs (mean holdout 28.9%, worst 22.9%, mean DSR 0.194)
- FAMILY `sma_trend` has the best median holdout CAGR (21.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.6%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.8%) - add more parameters to it


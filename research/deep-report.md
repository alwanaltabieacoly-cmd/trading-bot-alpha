# Deep research report

- Runs analysed: **18**
- Candidates per run: ~124
- Cumulative candidates evaluated: **2,232**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-23 15:12:09+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3061** (min 0.1793, max 0.612, over 18 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.5% | 20.4% | -16.4% | 0.145 | 0.202 | 198 | 0 |
| `sma_trend_vol_filter` | 14.4% | 14.1% | -10.5% | 0.117 | 0.563 | 597 | 0 |
| `sma_trend_efficiency` | 13.3% | 12.2% | -13.7% | 0.231 | 0.472 | 225 | 0 |
| `ema_trend` | 10.9% | 11.6% | -15.1% | 0.108 | 0.155 | 108 | 0 |
| `ema_trend_regime` | 8.3% | 8.7% | -11.1% | 0.054 | 0.183 | 140 | 0 |
| `sma_trend_fast_slow` | 5.9% | 8.4% | -16.5% | 0.119 | 0.213 | 183 | 0 |
| `sma_trend_slope` | 7.2% | 7.5% | -14.2% | 0.097 | 0.173 | 156 | 0 |
| `sma_trend_confirm` | 6.1% | 2.8% | -16.5% | 0.089 | 0.168 | 92 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.3% | 0.305 | 0.429 | 36 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.096 | 0.311 | 36 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 18 | 18 | 29.5% | 28.1% | 0.138 | 9.2 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 18 | 18 | 28.8% | 27.4% | 0.370 | 8.2 |
| `sma_trend_period50` | 18 | 18 | 27.3% | 25.9% | 0.189 | 8.2 |
| `sma_trend_period175` | 18 | 18 | 27.0% | 25.7% | 0.108 | 8.2 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 18 | 18 | 26.8% | 25.5% | 0.401 | 7.2 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 18 | 18 | 26.2% | 25.0% | 0.108 | 9.2 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 15 | 15 | 25.7% | 22.7% | 0.152 | 9.2 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 18 | 18 | 25.3% | 24.5% | 0.410 | 10.2 |
| `sma_trend_period225` | 18 | 18 | 24.5% | 23.1% | 0.135 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 18 | 18 | 24.1% | 22.7% | 0.384 | 8.2 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 18 | 7.0% | -6.1% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 15 | 4.9% | -2.4% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 15 | 6.8% | -1.9% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 18/18 runs (mean holdout 29.5%, worst 28.1%, mean DSR 0.138)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 18/18 runs (mean holdout 28.8%, worst 27.4%, mean DSR 0.370)
- KEEP: `sma_trend_period50` was positive in 18/18 runs (mean holdout 27.3%, worst 25.9%, mean DSR 0.189)
- KEEP: `sma_trend_period175` was positive in 18/18 runs (mean holdout 27.0%, worst 25.7%, mean DSR 0.108)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 18/18 runs (mean holdout 26.8%, worst 25.5%, mean DSR 0.401)
- FAMILY `sma_trend` has the best median holdout CAGR (20.4%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.2%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.6%) - add more parameters to it


# Deep research report

- Runs analysed: **20**
- Candidates per run: ~124
- Cumulative candidates evaluated: **2,516**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-23 23:14:36+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3318** (min 0.1793, max 0.612, over 20 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.8% | 20.5% | -16.4% | 0.148 | 0.202 | 220 | 0 |
| `sma_trend_vol_filter` | 14.5% | 14.1% | -10.4% | 0.120 | 0.569 | 665 | 0 |
| `sma_trend_efficiency` | 13.3% | 12.3% | -13.7% | 0.237 | 0.478 | 255 | 0 |
| `ema_trend` | 11.3% | 12.1% | -15.1% | 0.108 | 0.155 | 120 | 0 |
| `ema_trend_regime` | 8.5% | 8.7% | -11.1% | 0.056 | 0.187 | 158 | 0 |
| `sma_trend_fast_slow` | 6.1% | 8.4% | -16.4% | 0.121 | 0.217 | 205 | 0 |
| `sma_trend_slope` | 7.6% | 7.6% | -14.2% | 0.099 | 0.177 | 180 | 0 |
| `sma_trend_confirm` | 6.5% | 3.1% | -16.5% | 0.090 | 0.172 | 108 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.3% | 0.304 | 0.429 | 40 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.093 | 0.311 | 40 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 20 | 20 | 29.7% | 28.1% | 0.141 | 9.2 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 20 | 20 | 29.1% | 27.4% | 0.380 | 8.2 |
| `sma_trend_period50` | 20 | 20 | 27.3% | 25.9% | 0.190 | 8.2 |
| `sma_trend_period175` | 20 | 20 | 27.3% | 25.7% | 0.110 | 8.2 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 20 | 20 | 27.1% | 25.5% | 0.410 | 7.2 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 20 | 20 | 26.5% | 25.0% | 0.118 | 9.2 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 20 | 20 | 25.4% | 24.5% | 0.415 | 10.2 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 17 | 17 | 25.3% | 22.4% | 0.160 | 9.3 |
| `sma_trend_period225` | 20 | 20 | 24.9% | 23.1% | 0.138 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 20 | 20 | 24.5% | 22.7% | 0.394 | 8.2 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 20 | 7.0% | -5.8% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 17 | 6.8% | -1.8% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 15 | 4.9% | -2.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 20/20 runs (mean holdout 29.7%, worst 28.1%, mean DSR 0.141)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 20/20 runs (mean holdout 29.1%, worst 27.4%, mean DSR 0.380)
- KEEP: `sma_trend_period50` was positive in 20/20 runs (mean holdout 27.3%, worst 25.9%, mean DSR 0.190)
- KEEP: `sma_trend_period175` was positive in 20/20 runs (mean holdout 27.3%, worst 25.7%, mean DSR 0.110)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 20/20 runs (mean holdout 27.1%, worst 25.5%, mean DSR 0.410)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.1%) - add more parameters to it


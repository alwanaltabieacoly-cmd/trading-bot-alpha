# Deep research report

- Runs analysed: **27**
- Candidates per run: ~124
- Cumulative candidates evaluated: **3,510**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-25 16:31:48+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3879** (min 0.1793, max 0.612, over 27 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.3% | 20.7% | -16.4% | 0.153 | 0.203 | 297 | 0 |
| `sma_trend_vol_filter` | 14.7% | 14.1% | -10.4% | 0.127 | 0.569 | 903 | 0 |
| `sma_trend_efficiency` | 13.1% | 12.3% | -13.7% | 0.249 | 0.478 | 360 | 0 |
| `ema_trend` | 11.9% | 12.3% | -15.2% | 0.110 | 0.155 | 162 | 0 |
| `ema_trend_regime` | 9.1% | 9.3% | -11.1% | 0.060 | 0.187 | 221 | 0 |
| `sma_trend_fast_slow` | 6.7% | 8.8% | -16.4% | 0.126 | 0.217 | 278 | 0 |
| `sma_trend_slope` | 8.3% | 8.8% | -14.2% | 0.103 | 0.177 | 263 | 0 |
| `sma_trend_confirm` | 7.2% | 5.0% | -16.5% | 0.094 | 0.172 | 164 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.2% | 0.303 | 0.429 | 54 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 0.9% | -3.0% | 0.087 | 0.311 | 54 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 27 | 27 | 30.1% | 28.1% | 0.149 | 9.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 27 | 27 | 29.6% | 27.4% | 0.405 | 8.4 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 27 | 27 | 27.6% | 25.5% | 0.430 | 7.4 |
| `sma_trend_period175` | 27 | 27 | 27.6% | 25.7% | 0.116 | 8.4 |
| `sma_trend_period50` | 27 | 27 | 27.4% | 25.4% | 0.192 | 8.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 27 | 27 | 26.9% | 25.0% | 0.142 | 9.4 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 27 | 27 | 25.6% | 24.5% | 0.425 | 10.4 |
| `sma_trend_period225` | 27 | 27 | 25.3% | 23.1% | 0.146 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 27 | 27 | 25.1% | 22.7% | 0.418 | 8.4 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 24 | 24 | 24.3% | 21.3% | 0.177 | 9.5 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 27 | 6.9% | -4.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 24 | 6.8% | -1.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 27/27 runs (mean holdout 30.1%, worst 28.1%, mean DSR 0.149)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 27/27 runs (mean holdout 29.6%, worst 27.4%, mean DSR 0.405)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 27/27 runs (mean holdout 27.6%, worst 25.5%, mean DSR 0.430)
- KEEP: `sma_trend_period175` was positive in 27/27 runs (mean holdout 27.6%, worst 25.7%, mean DSR 0.116)
- KEEP: `sma_trend_period50` was positive in 27/27 runs (mean holdout 27.4%, worst 25.4%, mean DSR 0.192)
- FAMILY `sma_trend` has the best median holdout CAGR (20.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.3%) - add more parameters to it


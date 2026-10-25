# Deep research report

- Runs analysed: **26**
- Candidates per run: ~124
- Cumulative candidates evaluated: **3,368**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-25 11:48:22+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3817** (min 0.1793, max 0.612, over 26 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.2% | 20.5% | -16.4% | 0.152 | 0.203 | 286 | 0 |
| `sma_trend_vol_filter` | 14.6% | 14.1% | -10.4% | 0.126 | 0.569 | 869 | 0 |
| `sma_trend_efficiency` | 13.1% | 12.3% | -13.7% | 0.248 | 0.478 | 345 | 0 |
| `ema_trend` | 11.8% | 12.3% | -15.2% | 0.110 | 0.155 | 156 | 0 |
| `ema_trend_regime` | 9.0% | 9.1% | -11.1% | 0.060 | 0.187 | 212 | 0 |
| `sma_trend_fast_slow` | 6.6% | 8.8% | -16.4% | 0.125 | 0.217 | 267 | 0 |
| `sma_trend_slope` | 8.2% | 8.4% | -14.2% | 0.103 | 0.177 | 251 | 0 |
| `sma_trend_confirm` | 7.1% | 4.8% | -16.5% | 0.093 | 0.172 | 156 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.2% | 0.303 | 0.429 | 52 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 0.9% | -3.0% | 0.088 | 0.311 | 52 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 26 | 26 | 30.0% | 28.1% | 0.148 | 9.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 26 | 26 | 29.5% | 27.4% | 0.402 | 8.4 |
| `sma_trend_period175` | 26 | 26 | 27.5% | 25.7% | 0.115 | 8.4 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 26 | 26 | 27.5% | 25.5% | 0.428 | 7.4 |
| `sma_trend_period50` | 26 | 26 | 27.3% | 25.4% | 0.192 | 8.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 26 | 26 | 26.8% | 25.0% | 0.139 | 9.4 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 26 | 26 | 25.5% | 24.5% | 0.424 | 10.4 |
| `sma_trend_period225` | 26 | 26 | 25.2% | 23.1% | 0.145 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 26 | 26 | 25.0% | 22.7% | 0.416 | 8.4 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 23 | 23 | 24.4% | 21.3% | 0.176 | 9.5 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 26 | 6.9% | -5.1% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 23 | 6.8% | -1.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 26/26 runs (mean holdout 30.0%, worst 28.1%, mean DSR 0.148)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 26/26 runs (mean holdout 29.5%, worst 27.4%, mean DSR 0.402)
- KEEP: `sma_trend_period175` was positive in 26/26 runs (mean holdout 27.5%, worst 25.7%, mean DSR 0.115)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 26/26 runs (mean holdout 27.5%, worst 25.5%, mean DSR 0.428)
- KEEP: `sma_trend_period50` was positive in 26/26 runs (mean holdout 27.3%, worst 25.4%, mean DSR 0.192)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.3%) - add more parameters to it


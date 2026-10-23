# Deep research report

- Runs analysed: **19**
- Candidates per run: ~124
- Cumulative candidates evaluated: **2,374**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-23 19:21:57+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3197** (min 0.1793, max 0.612, over 19 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.7% | 20.5% | -16.4% | 0.147 | 0.202 | 209 | 0 |
| `sma_trend_vol_filter` | 14.5% | 14.1% | -10.4% | 0.118 | 0.569 | 631 | 0 |
| `sma_trend_efficiency` | 13.3% | 12.3% | -13.7% | 0.234 | 0.478 | 240 | 0 |
| `ema_trend` | 11.1% | 11.6% | -15.1% | 0.108 | 0.155 | 114 | 0 |
| `ema_trend_regime` | 8.4% | 8.7% | -11.1% | 0.055 | 0.187 | 149 | 0 |
| `sma_trend_fast_slow` | 6.0% | 8.4% | -16.4% | 0.120 | 0.217 | 194 | 0 |
| `sma_trend_slope` | 7.4% | 7.5% | -14.2% | 0.098 | 0.177 | 168 | 0 |
| `sma_trend_confirm` | 6.3% | 3.0% | -16.5% | 0.090 | 0.172 | 100 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.3% | 0.305 | 0.429 | 38 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.094 | 0.311 | 38 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 19 | 19 | 29.6% | 28.1% | 0.140 | 9.2 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 19 | 19 | 29.0% | 27.4% | 0.375 | 8.2 |
| `sma_trend_period50` | 19 | 19 | 27.3% | 25.9% | 0.189 | 8.2 |
| `sma_trend_period175` | 19 | 19 | 27.2% | 25.7% | 0.109 | 8.2 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 19 | 19 | 26.9% | 25.5% | 0.406 | 7.2 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 19 | 19 | 26.4% | 25.0% | 0.114 | 9.2 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 16 | 16 | 25.5% | 22.5% | 0.157 | 9.2 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 19 | 19 | 25.3% | 24.5% | 0.413 | 10.2 |
| `sma_trend_period225` | 19 | 19 | 24.7% | 23.1% | 0.137 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 19 | 19 | 24.3% | 22.7% | 0.390 | 8.2 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 19 | 7.0% | -5.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 16 | 6.8% | -1.8% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 15 | 4.9% | -2.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 19/19 runs (mean holdout 29.6%, worst 28.1%, mean DSR 0.140)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 19/19 runs (mean holdout 29.0%, worst 27.4%, mean DSR 0.375)
- KEEP: `sma_trend_period50` was positive in 19/19 runs (mean holdout 27.3%, worst 25.9%, mean DSR 0.189)
- KEEP: `sma_trend_period175` was positive in 19/19 runs (mean holdout 27.2%, worst 25.7%, mean DSR 0.109)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 19/19 runs (mean holdout 26.9%, worst 25.5%, mean DSR 0.406)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.6%) - add more parameters to it


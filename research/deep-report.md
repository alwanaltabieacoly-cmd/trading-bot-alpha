# Deep research report

- Runs analysed: **17**
- Candidates per run: ~124
- Cumulative candidates evaluated: **2,084**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-23 10:12:28+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.2881** (min 0.1793, max 0.612, over 17 runs)
- Verdict: **search is weakly informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.3% | 18.8% | -16.4% | 0.144 | 0.202 | 187 | 0 |
| `sma_trend_vol_filter` | 14.4% | 14.1% | -10.5% | 0.115 | 0.563 | 563 | 0 |
| `sma_trend_efficiency` | 13.4% | 12.2% | -13.7% | 0.228 | 0.472 | 210 | 0 |
| `ema_trend` | 10.6% | 11.6% | -15.2% | 0.108 | 0.155 | 102 | 0 |
| `ema_trend_regime` | 8.1% | 8.4% | -11.2% | 0.053 | 0.183 | 131 | 0 |
| `sma_trend_fast_slow` | 5.8% | 8.4% | -16.5% | 0.118 | 0.213 | 172 | 0 |
| `sma_trend_slope` | 6.9% | 7.5% | -14.2% | 0.097 | 0.173 | 144 | 0 |
| `sma_trend_confirm` | 5.8% | 2.7% | -16.5% | 0.088 | 0.168 | 84 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.3% | 0.306 | 0.429 | 34 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.097 | 0.311 | 34 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 2 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 17 | 17 | 29.3% | 28.1% | 0.136 | 9.1 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 17 | 17 | 28.6% | 27.4% | 0.364 | 8.1 |
| `sma_trend_period50` | 17 | 17 | 27.3% | 25.9% | 0.188 | 8.1 |
| `sma_trend_period175` | 17 | 17 | 26.9% | 25.7% | 0.107 | 8.1 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 17 | 17 | 26.6% | 25.5% | 0.397 | 7.1 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 17 | 17 | 26.1% | 25.0% | 0.103 | 9.1 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 14 | 14 | 25.9% | 22.7% | 0.148 | 9.1 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 17 | 17 | 25.2% | 24.5% | 0.408 | 10.1 |
| `sma_trend_period225` | 17 | 17 | 24.3% | 23.1% | 0.133 | 9.1 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 17 | 17 | 23.9% | 22.7% | 0.379 | 8.1 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 17 | 7.1% | -6.3% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 15 | 4.9% | -2.4% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 14 | 6.8% | -2.0% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |
| `sma_trend_rsi_filter_period250_rsi_period14_rsi_max80` | 3 | 12.2% | -5.4% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 17/17 runs (mean holdout 29.3%, worst 28.1%, mean DSR 0.136)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 17/17 runs (mean holdout 28.6%, worst 27.4%, mean DSR 0.364)
- KEEP: `sma_trend_period50` was positive in 17/17 runs (mean holdout 27.3%, worst 25.9%, mean DSR 0.188)
- KEEP: `sma_trend_period175` was positive in 17/17 runs (mean holdout 26.9%, worst 25.7%, mean DSR 0.107)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 17/17 runs (mean holdout 26.6%, worst 25.5%, mean DSR 0.397)
- FAMILY `sma_trend` has the best median holdout CAGR (18.8%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.2%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.6%) - add more parameters to it


# Deep research report

- Runs analysed: **16**
- Candidates per run: ~124
- Cumulative candidates evaluated: **1,936**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-23 05:01:17+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.2678** (min 0.1793, max 0.612, over 16 runs)
- Verdict: **search is weakly informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.1% | 18.8% | -16.4% | 0.143 | 0.202 | 176 | 0 |
| `sma_trend_vol_filter` | 14.3% | 14.1% | -10.5% | 0.113 | 0.563 | 529 | 0 |
| `sma_trend_efficiency` | 13.4% | 12.2% | -13.7% | 0.224 | 0.472 | 195 | 0 |
| `ema_trend` | 10.3% | 11.6% | -15.2% | 0.108 | 0.155 | 96 | 0 |
| `ema_trend_regime` | 7.9% | 8.4% | -11.2% | 0.052 | 0.183 | 122 | 0 |
| `sma_trend_fast_slow` | 5.6% | 8.4% | -16.5% | 0.117 | 0.213 | 161 | 0 |
| `sma_trend_slope` | 6.6% | 7.5% | -14.2% | 0.096 | 0.173 | 132 | 0 |
| `sma_trend_confirm` | 5.4% | 1.8% | -16.6% | 0.087 | 0.168 | 76 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.3% | 0.306 | 0.429 | 32 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.099 | 0.311 | 32 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 1 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 16 | 16 | 29.1% | 28.1% | 0.134 | 9.1 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 16 | 16 | 28.4% | 27.4% | 0.357 | 8.1 |
| `sma_trend_period50` | 16 | 16 | 27.3% | 25.9% | 0.188 | 8.1 |
| `sma_trend_period175` | 16 | 16 | 26.7% | 25.7% | 0.105 | 8.1 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 16 | 16 | 26.4% | 25.5% | 0.392 | 7.1 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 13 | 13 | 26.1% | 22.7% | 0.143 | 9.1 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 16 | 16 | 25.9% | 25.0% | 0.096 | 9.1 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 16 | 16 | 25.2% | 24.5% | 0.406 | 10.1 |
| `sma_trend_period225` | 16 | 16 | 24.1% | 23.1% | 0.131 | 9.1 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 16 | 16 | 23.7% | 22.7% | 0.372 | 8.1 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 16 | 7.1% | -6.4% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 15 | 4.9% | -2.4% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 13 | 6.7% | -2.1% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |
| `sma_trend_rsi_filter_period250_rsi_period14_rsi_max80` | 3 | 12.2% | -5.4% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 16/16 runs (mean holdout 29.1%, worst 28.1%, mean DSR 0.134)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 16/16 runs (mean holdout 28.4%, worst 27.4%, mean DSR 0.357)
- KEEP: `sma_trend_period50` was positive in 16/16 runs (mean holdout 27.3%, worst 25.9%, mean DSR 0.188)
- KEEP: `sma_trend_period175` was positive in 16/16 runs (mean holdout 26.7%, worst 25.7%, mean DSR 0.105)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 16/16 runs (mean holdout 26.4%, worst 25.5%, mean DSR 0.392)
- FAMILY `sma_trend` has the best median holdout CAGR (18.8%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.2%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.6%) - add more parameters to it


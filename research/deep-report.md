# Deep research report

- Runs analysed: **23**
- Candidates per run: ~124
- Cumulative candidates evaluated: **2,942**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-24 16:41:36+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3601** (min 0.1793, max 0.612, over 23 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.9% | 20.5% | -16.4% | 0.150 | 0.202 | 253 | 0 |
| `sma_trend_vol_filter` | 14.5% | 14.0% | -10.4% | 0.124 | 0.569 | 767 | 0 |
| `sma_trend_efficiency` | 13.1% | 12.3% | -13.7% | 0.243 | 0.478 | 300 | 0 |
| `ema_trend` | 11.5% | 12.2% | -15.1% | 0.109 | 0.155 | 138 | 0 |
| `sma_trend_fast_slow` | 6.2% | 8.7% | -16.4% | 0.123 | 0.217 | 235 | 0 |
| `ema_trend_regime` | 8.7% | 8.7% | -11.1% | 0.058 | 0.187 | 185 | 0 |
| `sma_trend_slope` | 7.8% | 8.3% | -14.2% | 0.101 | 0.177 | 216 | 0 |
| `sma_trend_confirm` | 6.8% | 4.6% | -16.5% | 0.092 | 0.172 | 132 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.2% | 0.303 | 0.429 | 46 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.090 | 0.311 | 46 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 23 | 23 | 29.8% | 28.1% | 0.145 | 9.3 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 23 | 23 | 29.2% | 27.4% | 0.393 | 8.3 |
| `sma_trend_period175` | 23 | 23 | 27.3% | 25.7% | 0.113 | 8.3 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 23 | 23 | 27.2% | 25.5% | 0.420 | 7.3 |
| `sma_trend_period50` | 23 | 23 | 27.1% | 25.4% | 0.191 | 8.3 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 23 | 23 | 26.5% | 25.0% | 0.130 | 9.3 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 23 | 23 | 25.3% | 24.5% | 0.420 | 10.3 |
| `sma_trend_period225` | 23 | 23 | 25.0% | 23.1% | 0.142 | 9.3 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 20 | 20 | 24.8% | 22.0% | 0.169 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 23 | 23 | 24.7% | 22.7% | 0.406 | 8.3 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 23 | 7.0% | -5.5% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 20 | 6.8% | -1.7% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 18 | 5.0% | -2.0% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 23/23 runs (mean holdout 29.8%, worst 28.1%, mean DSR 0.145)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 23/23 runs (mean holdout 29.2%, worst 27.4%, mean DSR 0.393)
- KEEP: `sma_trend_period175` was positive in 23/23 runs (mean holdout 27.3%, worst 25.7%, mean DSR 0.113)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 23/23 runs (mean holdout 27.2%, worst 25.5%, mean DSR 0.420)
- KEEP: `sma_trend_period50` was positive in 23/23 runs (mean holdout 27.1%, worst 25.4%, mean DSR 0.191)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.2%) - add more parameters to it


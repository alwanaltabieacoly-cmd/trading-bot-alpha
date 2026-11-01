# Deep research report

- Runs analysed: **53**
- Candidates per run: ~142
- Cumulative candidates evaluated: **7,202**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-01 01:18:54+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4419** (min 0.1793, max 0.612, over 53 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 22.0% | 22.1% | -16.6% | 0.160 | 0.203 | 583 | 0 |
| `sma_trend_vol_filter` | 16.4% | 15.7% | -10.4% | 0.138 | 0.579 | 1762 | 0 |
| `ema_trend` | 13.2% | 14.1% | -15.5% | 0.112 | 0.155 | 318 | 0 |
| `sma_trend_efficiency` | 12.9% | 13.2% | -13.9% | 0.264 | 0.478 | 756 | 0 |
| `ema_trend_regime` | 10.7% | 10.7% | -11.2% | 0.067 | 0.202 | 455 | 0 |
| `sma_trend_slope` | 9.5% | 10.6% | -14.6% | 0.108 | 0.179 | 574 | 0 |
| `sma_trend_fast_slow` | 8.5% | 9.8% | -16.3% | 0.133 | 0.221 | 573 | 0 |
| `sma_trend_confirm` | 8.7% | 6.8% | -16.7% | 0.098 | 0.174 | 364 | 0 |
| `donchian_trend` | 2.5% | 2.0% | -4.2% | 0.300 | 0.429 | 106 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.079 | 0.311 | 107 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 53 | 53 | 31.8% | 27.4% | 0.441 | 8.7 |
| `sma_trend_period200` | 53 | 53 | 31.5% | 28.1% | 0.160 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 53 | 53 | 29.8% | 25.5% | 0.460 | 8.5 |
| `sma_trend_period50` | 53 | 53 | 29.2% | 25.4% | 0.193 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 53 | 53 | 29.2% | 25.0% | 0.177 | 9.7 |
| `sma_trend_period175` | 53 | 53 | 29.0% | 25.7% | 0.124 | 9.0 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 53 | 53 | 27.5% | 22.7% | 0.453 | 8.7 |
| `sma_trend_period225` | 53 | 53 | 27.0% | 23.1% | 0.156 | 9.5 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 53 | 53 | 26.9% | 24.5% | 0.436 | 10.5 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 53 | 53 | 25.2% | 20.7% | 0.101 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 44 | 6.7% | -3.2% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 14 | 13.4% | -1.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 12 | 10.1% | -0.2% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 53/53 runs (mean holdout 31.8%, worst 27.4%, mean DSR 0.441)
- KEEP: `sma_trend_period200` was positive in 53/53 runs (mean holdout 31.5%, worst 28.1%, mean DSR 0.160)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 53/53 runs (mean holdout 29.8%, worst 25.5%, mean DSR 0.460)
- KEEP: `sma_trend_period50` was positive in 53/53 runs (mean holdout 29.2%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 53/53 runs (mean holdout 29.2%, worst 25.0%, mean DSR 0.177)
- FAMILY `sma_trend` has the best median holdout CAGR (22.1%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.2%) - add more parameters to it


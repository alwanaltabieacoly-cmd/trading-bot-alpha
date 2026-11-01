# Deep research report

- Runs analysed: **56**
- Candidates per run: ~142
- Cumulative candidates evaluated: **7,628**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-01 19:51:10+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.443** (min 0.1793, max 0.612, over 56 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 22.0% | 22.0% | -16.6% | 0.160 | 0.203 | 616 | 0 |
| `sma_trend_vol_filter` | 16.4% | 15.7% | -10.4% | 0.139 | 0.579 | 1861 | 0 |
| `ema_trend` | 13.1% | 14.1% | -15.6% | 0.112 | 0.155 | 336 | 0 |
| `sma_trend_efficiency` | 12.9% | 13.2% | -13.9% | 0.265 | 0.478 | 804 | 0 |
| `ema_trend_regime` | 10.7% | 10.7% | -11.2% | 0.067 | 0.202 | 482 | 0 |
| `sma_trend_slope` | 9.5% | 10.6% | -14.6% | 0.108 | 0.179 | 610 | 0 |
| `sma_trend_fast_slow` | 8.6% | 9.9% | -16.3% | 0.134 | 0.221 | 609 | 0 |
| `sma_trend_confirm` | 8.6% | 6.8% | -16.8% | 0.098 | 0.174 | 385 | 0 |
| `donchian_trend` | 2.5% | 2.0% | -4.1% | 0.300 | 0.429 | 112 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 1.1% | -3.0% | 0.078 | 0.311 | 116 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 56 | 56 | 31.9% | 27.4% | 0.443 | 8.7 |
| `sma_trend_period200` | 56 | 56 | 31.5% | 28.1% | 0.161 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 56 | 56 | 29.9% | 25.5% | 0.462 | 8.6 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 56 | 56 | 29.3% | 25.0% | 0.179 | 9.7 |
| `sma_trend_period50` | 56 | 56 | 29.3% | 25.4% | 0.193 | 8.9 |
| `sma_trend_period175` | 56 | 56 | 29.1% | 25.7% | 0.125 | 9.1 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 56 | 56 | 27.6% | 22.7% | 0.455 | 8.7 |
| `sma_trend_period225` | 56 | 56 | 26.9% | 23.1% | 0.157 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 56 | 56 | 26.9% | 24.5% | 0.438 | 10.5 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 56 | 56 | 25.3% | 20.7% | 0.103 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 44 | 6.7% | -3.2% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_confirm_slow_period100_fast_period50` | 15 | 10.0% | -0.3% |
| `sma_trend_slope_period100_slope_bars10` | 14 | 13.4% | -1.4% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 56/56 runs (mean holdout 31.9%, worst 27.4%, mean DSR 0.443)
- KEEP: `sma_trend_period200` was positive in 56/56 runs (mean holdout 31.5%, worst 28.1%, mean DSR 0.161)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 56/56 runs (mean holdout 29.9%, worst 25.5%, mean DSR 0.462)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 56/56 runs (mean holdout 29.3%, worst 25.0%, mean DSR 0.179)
- KEEP: `sma_trend_period50` was positive in 56/56 runs (mean holdout 29.3%, worst 25.4%, mean DSR 0.193)
- FAMILY `sma_trend` has the best median holdout CAGR (22.0%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.2%) - add more parameters to it


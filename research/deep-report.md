# Deep research report

- Runs analysed: **79**
- Candidates per run: ~142
- Cumulative candidates evaluated: **10,894**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-08 09:11:03+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4278** (min 0.1793, max 0.612, over 79 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.5% | 20.6% | -16.9% | 0.164 | 0.226 | 869 | 0 |
| `sma_trend_vol_filter` | 15.8% | 15.2% | -10.4% | 0.145 | 0.607 | 2610 | 0 |
| `ema_trend` | 11.8% | 12.7% | -15.9% | 0.113 | 0.155 | 466 | 0 |
| `sma_trend_efficiency` | 12.5% | 12.7% | -14.0% | 0.270 | 0.488 | 1172 | 0 |
| `ema_trend_regime` | 10.0% | 10.0% | -11.3% | 0.071 | 0.241 | 685 | 0 |
| `sma_trend_slope` | 8.4% | 8.8% | -15.0% | 0.110 | 0.183 | 851 | 0 |
| `sma_trend_fast_slow` | 7.8% | 8.8% | -16.3% | 0.137 | 0.226 | 843 | 0 |
| `sma_trend_confirm` | 7.6% | 5.9% | -17.0% | 0.100 | 0.178 | 519 | 0 |
| `donchian_trend` | 2.8% | 2.0% | -4.1% | 0.300 | 0.429 | 177 | 0 |
| `donchian_trend_vol_filter` | 1.7% | 1.2% | -2.9% | 0.076 | 0.311 | 170 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 79 | 79 | 31.1% | 24.7% | 0.458 | 8.8 |
| `sma_trend_period200` | 79 | 79 | 30.0% | 21.4% | 0.165 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 79 | 79 | 29.0% | 21.2% | 0.474 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 79 | 79 | 28.6% | 22.9% | 0.195 | 9.8 |
| `sma_trend_period175` | 79 | 79 | 27.6% | 17.4% | 0.128 | 9.3 |
| `sma_trend_period50` | 79 | 79 | 27.0% | 13.2% | 0.198 | 8.8 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 79 | 79 | 26.5% | 19.6% | 0.469 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 79 | 79 | 25.9% | 17.2% | 0.452 | 10.1 |
| `sma_trend_period225` | 79 | 79 | 25.3% | 16.2% | 0.161 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 79 | 79 | 24.3% | 18.1% | 0.114 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 66 | 6.6% | -3.4% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 38 | 9.9% | -1.5% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 27 | 5.0% | -2.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 26 | 9.8% | -1.4% |
| `sma_trend_slope_period100_slope_bars10` | 25 | 12.9% | -1.4% |
| `sma_trend_slope_period150_slope_bars40` | 24 | 12.6% | -3.3% |
| `sma_trend_confirm_slow_period150_fast_period50` | 19 | 12.1% | -0.9% |
| `ema_trend_fast50_slow300` | 8 | 8.1% | -2.7% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 6 | 11.4% | -1.8% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 79/79 runs (mean holdout 31.1%, worst 24.7%, mean DSR 0.458)
- KEEP: `sma_trend_period200` was positive in 79/79 runs (mean holdout 30.0%, worst 21.4%, mean DSR 0.165)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 79/79 runs (mean holdout 29.0%, worst 21.2%, mean DSR 0.474)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 79/79 runs (mean holdout 28.6%, worst 22.9%, mean DSR 0.195)
- KEEP: `sma_trend_period175` was positive in 79/79 runs (mean holdout 27.6%, worst 17.4%, mean DSR 0.128)
- FAMILY `sma_trend` has the best median holdout CAGR (20.6%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.2%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.7%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it


# Deep research report

- Runs analysed: **123**
- Candidates per run: ~142
- Cumulative candidates evaluated: **17,142**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-21 11:24:58+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3853** (min 0.1793, max 0.612, over 123 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.5% | -17.1% | 0.167 | 0.226 | 1353 | 0 |
| `sma_trend_vol_filter` | 15.9% | 15.7% | -10.1% | 0.153 | 0.607 | 4037 | 0 |
| `sma_trend_efficiency` | 12.4% | 13.3% | -14.2% | 0.277 | 0.499 | 1876 | 0 |
| `ema_trend` | 10.4% | 10.6% | -16.5% | 0.115 | 0.155 | 715 | 0 |
| `ema_trend_regime` | 10.0% | 9.8% | -11.1% | 0.077 | 0.243 | 1065 | 0 |
| `sma_trend_fast_slow` | 7.3% | 8.1% | -16.4% | 0.141 | 0.233 | 1273 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.2% | 0.113 | 0.186 | 1323 | 0 |
| `sma_trend_confirm` | 7.0% | 5.5% | -17.0% | 0.102 | 0.181 | 834 | 0 |
| `donchian_trend` | 3.7% | 2.7% | -3.9% | 0.298 | 0.429 | 309 | 0 |
| `donchian_trend_vol_filter` | 2.4% | 2.3% | -2.7% | 0.072 | 0.311 | 260 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 123 | 123 | 30.6% | 24.7% | 0.475 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 123 | 123 | 28.6% | 22.9% | 0.215 | 9.9 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 123 | 123 | 28.1% | 21.2% | 0.488 | 9.1 |
| `sma_trend_period200` | 123 | 123 | 28.1% | 20.5% | 0.169 | 9.3 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 123 | 123 | 26.1% | 19.6% | 0.486 | 8.6 |
| `sma_trend_period50` | 123 | 123 | 26.0% | 13.2% | 0.201 | 8.7 |
| `sma_trend_period175` | 123 | 123 | 25.2% | 16.9% | 0.131 | 9.4 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 123 | 123 | 25.1% | 17.2% | 0.473 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 123 | 123 | 24.3% | 18.1% | 0.128 | 8.7 |
| `sma_trend_period225` | 123 | 123 | 23.5% | 16.2% | 0.165 | 8.8 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 110 | 6.5% | -3.4% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 71 | 5.0% | -2.0% |
| `sma_trend_slope_period150_slope_bars40` | 68 | 12.1% | -2.8% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 123/123 runs (mean holdout 30.6%, worst 24.7%, mean DSR 0.475)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 123/123 runs (mean holdout 28.6%, worst 22.9%, mean DSR 0.215)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 123/123 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.488)
- KEEP: `sma_trend_period200` was positive in 123/123 runs (mean holdout 28.1%, worst 20.5%, mean DSR 0.169)
- KEEP: `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` was positive in 123/123 runs (mean holdout 26.1%, worst 19.6%, mean DSR 0.486)
- FAMILY `sma_trend` has the best median holdout CAGR (19.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.7%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (10.6%) - add more parameters to it


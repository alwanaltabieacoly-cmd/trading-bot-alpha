# Deep research report

- Runs analysed: **105**
- Candidates per run: ~142
- Cumulative candidates evaluated: **14,586**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-15 17:52:51+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.397** (min 0.1793, max 0.612, over 105 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.7% | -17.0% | 0.166 | 0.226 | 1155 | 0 |
| `sma_trend_vol_filter` | 15.6% | 15.2% | -10.2% | 0.151 | 0.607 | 3475 | 0 |
| `sma_trend_efficiency` | 12.3% | 13.1% | -14.2% | 0.275 | 0.493 | 1588 | 0 |
| `ema_trend` | 10.7% | 11.1% | -16.2% | 0.114 | 0.155 | 607 | 0 |
| `ema_trend_regime` | 9.7% | 9.6% | -11.2% | 0.075 | 0.243 | 921 | 0 |
| `sma_trend_fast_slow` | 7.2% | 8.1% | -16.4% | 0.140 | 0.229 | 1093 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.1% | 0.112 | 0.184 | 1125 | 0 |
| `sma_trend_confirm` | 6.9% | 5.3% | -17.1% | 0.101 | 0.179 | 690 | 0 |
| `donchian_trend` | 3.4% | 2.3% | -4.0% | 0.299 | 0.429 | 255 | 0 |
| `donchian_trend_vol_filter` | 2.2% | 1.8% | -2.8% | 0.073 | 0.311 | 224 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 105 | 105 | 30.4% | 24.7% | 0.469 | 8.8 |
| `sma_trend_period200` | 105 | 105 | 28.4% | 20.5% | 0.168 | 9.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 105 | 105 | 28.2% | 22.9% | 0.208 | 9.8 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 105 | 105 | 28.1% | 21.2% | 0.484 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 105 | 105 | 25.9% | 19.6% | 0.481 | 8.7 |
| `sma_trend_period50` | 105 | 105 | 25.7% | 13.2% | 0.202 | 8.7 |
| `sma_trend_period175` | 105 | 105 | 25.6% | 16.9% | 0.130 | 9.3 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 105 | 105 | 24.9% | 17.2% | 0.470 | 9.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 105 | 105 | 24.0% | 18.1% | 0.123 | 8.8 |
| `sma_trend_period225` | 105 | 105 | 23.8% | 16.2% | 0.164 | 9.1 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 92 | 6.6% | -3.6% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 53 | 5.0% | -2.4% |
| `sma_trend_slope_period150_slope_bars40` | 50 | 12.3% | -3.3% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 105/105 runs (mean holdout 30.4%, worst 24.7%, mean DSR 0.469)
- KEEP: `sma_trend_period200` was positive in 105/105 runs (mean holdout 28.4%, worst 20.5%, mean DSR 0.168)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 105/105 runs (mean holdout 28.2%, worst 22.9%, mean DSR 0.208)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 105/105 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.484)
- KEEP: `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` was positive in 105/105 runs (mean holdout 25.9%, worst 19.6%, mean DSR 0.481)
- FAMILY `sma_trend` has the best median holdout CAGR (19.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.2%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.1%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.1%) - add more parameters to it


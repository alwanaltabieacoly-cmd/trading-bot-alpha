# Deep research report

- Runs analysed: **106**
- Candidates per run: ~142
- Cumulative candidates evaluated: **14,728**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-15 22:59:37+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3965** (min 0.1793, max 0.612, over 106 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.7% | -17.0% | 0.166 | 0.226 | 1166 | 0 |
| `sma_trend_vol_filter` | 15.6% | 15.2% | -10.2% | 0.151 | 0.607 | 3507 | 0 |
| `sma_trend_efficiency` | 12.3% | 13.1% | -14.2% | 0.275 | 0.493 | 1604 | 0 |
| `ema_trend` | 10.7% | 11.0% | -16.3% | 0.114 | 0.155 | 613 | 0 |
| `ema_trend_regime` | 9.7% | 9.7% | -11.2% | 0.075 | 0.243 | 929 | 0 |
| `sma_trend_fast_slow` | 7.2% | 8.1% | -16.4% | 0.140 | 0.229 | 1103 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.1% | 0.112 | 0.184 | 1136 | 0 |
| `sma_trend_confirm` | 6.9% | 5.3% | -17.1% | 0.101 | 0.179 | 698 | 0 |
| `donchian_trend` | 3.4% | 2.3% | -4.0% | 0.299 | 0.429 | 258 | 0 |
| `donchian_trend_vol_filter` | 2.2% | 1.8% | -2.8% | 0.073 | 0.311 | 226 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 106 | 106 | 30.4% | 24.7% | 0.470 | 8.8 |
| `sma_trend_period200` | 106 | 106 | 28.4% | 20.5% | 0.168 | 9.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 106 | 106 | 28.2% | 22.9% | 0.208 | 9.8 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 106 | 106 | 28.1% | 21.2% | 0.484 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 106 | 106 | 25.9% | 19.6% | 0.481 | 8.7 |
| `sma_trend_period50` | 106 | 106 | 25.7% | 13.2% | 0.202 | 8.7 |
| `sma_trend_period175` | 106 | 106 | 25.6% | 16.9% | 0.130 | 9.3 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 106 | 106 | 24.9% | 17.2% | 0.470 | 9.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 106 | 106 | 24.0% | 18.1% | 0.123 | 8.8 |
| `sma_trend_period225` | 106 | 106 | 23.8% | 16.2% | 0.164 | 9.1 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 93 | 6.6% | -3.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 54 | 5.0% | -2.3% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_slope_period150_slope_bars40` | 51 | 12.2% | -3.3% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 106/106 runs (mean holdout 30.4%, worst 24.7%, mean DSR 0.470)
- KEEP: `sma_trend_period200` was positive in 106/106 runs (mean holdout 28.4%, worst 20.5%, mean DSR 0.168)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 106/106 runs (mean holdout 28.2%, worst 22.9%, mean DSR 0.208)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 106/106 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.484)
- KEEP: `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` was positive in 106/106 runs (mean holdout 25.9%, worst 19.6%, mean DSR 0.481)
- FAMILY `sma_trend` has the best median holdout CAGR (19.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.2%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.1%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.0%) - add more parameters to it


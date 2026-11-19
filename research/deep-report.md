# Deep research report

- Runs analysed: **118**
- Candidates per run: ~142
- Cumulative candidates evaluated: **16,432**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-19 22:18:12+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3885** (min 0.1793, max 0.612, over 118 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.5% | -17.1% | 0.167 | 0.226 | 1298 | 0 |
| `sma_trend_vol_filter` | 15.8% | 15.5% | -10.1% | 0.152 | 0.607 | 3882 | 0 |
| `sma_trend_efficiency` | 12.4% | 13.3% | -14.2% | 0.276 | 0.497 | 1796 | 0 |
| `ema_trend` | 10.5% | 10.6% | -16.4% | 0.115 | 0.155 | 685 | 0 |
| `ema_trend_regime` | 9.9% | 9.8% | -11.2% | 0.076 | 0.243 | 1025 | 0 |
| `sma_trend_fast_slow` | 7.3% | 8.1% | -16.4% | 0.141 | 0.230 | 1223 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.2% | 0.112 | 0.185 | 1268 | 0 |
| `sma_trend_confirm` | 7.0% | 5.4% | -17.0% | 0.102 | 0.180 | 794 | 0 |
| `donchian_trend` | 3.6% | 2.5% | -3.9% | 0.298 | 0.429 | 294 | 0 |
| `donchian_trend_vol_filter` | 2.4% | 2.1% | -2.7% | 0.072 | 0.311 | 250 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 118 | 118 | 30.6% | 24.7% | 0.473 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 118 | 118 | 28.5% | 22.9% | 0.213 | 9.8 |
| `sma_trend_period200` | 118 | 118 | 28.2% | 20.5% | 0.169 | 9.4 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 118 | 118 | 28.1% | 21.2% | 0.487 | 9.0 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 118 | 118 | 26.0% | 19.6% | 0.485 | 8.7 |
| `sma_trend_period50` | 118 | 118 | 25.9% | 13.2% | 0.201 | 8.7 |
| `sma_trend_period175` | 118 | 118 | 25.3% | 16.9% | 0.131 | 9.3 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 118 | 118 | 25.0% | 17.2% | 0.472 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 118 | 118 | 24.2% | 18.1% | 0.126 | 8.7 |
| `sma_trend_period225` | 118 | 118 | 23.5% | 16.2% | 0.165 | 8.9 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 105 | 6.5% | -3.5% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 66 | 5.0% | -2.1% |
| `sma_trend_slope_period150_slope_bars40` | 63 | 12.1% | -2.9% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 118/118 runs (mean holdout 30.6%, worst 24.7%, mean DSR 0.473)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 118/118 runs (mean holdout 28.5%, worst 22.9%, mean DSR 0.213)
- KEEP: `sma_trend_period200` was positive in 118/118 runs (mean holdout 28.2%, worst 20.5%, mean DSR 0.169)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 118/118 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.487)
- KEEP: `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` was positive in 118/118 runs (mean holdout 26.0%, worst 19.6%, mean DSR 0.485)
- FAMILY `sma_trend` has the best median holdout CAGR (19.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.5%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (10.6%) - add more parameters to it


# Deep research report

- Runs analysed: **80**
- Candidates per run: ~142
- Cumulative candidates evaluated: **11,036**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-08 16:06:21+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4257** (min 0.1793, max 0.612, over 80 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.4% | 20.5% | -16.9% | 0.164 | 0.226 | 880 | 0 |
| `sma_trend_vol_filter` | 15.8% | 15.2% | -10.4% | 0.145 | 0.607 | 2643 | 0 |
| `sma_trend_efficiency` | 12.5% | 12.7% | -14.0% | 0.271 | 0.488 | 1188 | 0 |
| `ema_trend` | 11.7% | 12.7% | -15.9% | 0.113 | 0.155 | 471 | 0 |
| `ema_trend_regime` | 10.0% | 9.9% | -11.3% | 0.072 | 0.241 | 695 | 0 |
| `sma_trend_slope` | 8.4% | 8.7% | -15.0% | 0.110 | 0.183 | 859 | 0 |
| `sma_trend_fast_slow` | 7.7% | 8.7% | -16.4% | 0.137 | 0.226 | 851 | 0 |
| `sma_trend_confirm` | 7.5% | 5.8% | -17.0% | 0.100 | 0.178 | 523 | 0 |
| `donchian_trend` | 2.8% | 2.0% | -4.0% | 0.300 | 0.429 | 180 | 0 |
| `donchian_trend_vol_filter` | 1.7% | 1.2% | -2.9% | 0.076 | 0.311 | 173 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 80 | 80 | 31.0% | 24.7% | 0.458 | 8.8 |
| `sma_trend_period200` | 80 | 80 | 29.9% | 21.4% | 0.165 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 80 | 80 | 29.0% | 21.2% | 0.475 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 80 | 80 | 28.5% | 22.9% | 0.195 | 9.8 |
| `sma_trend_period175` | 80 | 80 | 27.4% | 17.4% | 0.128 | 9.3 |
| `sma_trend_period50` | 80 | 80 | 26.8% | 13.2% | 0.198 | 8.8 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 80 | 80 | 26.4% | 19.6% | 0.470 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 80 | 80 | 25.8% | 17.2% | 0.453 | 10.1 |
| `sma_trend_period225` | 80 | 80 | 25.2% | 16.2% | 0.161 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 80 | 80 | 24.3% | 18.1% | 0.114 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 67 | 6.6% | -3.4% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 39 | 9.9% | -1.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 28 | 5.0% | -2.8% |
| `sma_trend_confirm_slow_period100_fast_period20` | 27 | 9.8% | -1.4% |
| `sma_trend_slope_period100_slope_bars10` | 26 | 12.8% | -1.5% |
| `sma_trend_slope_period150_slope_bars40` | 25 | 12.6% | -3.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 20 | 12.1% | -0.9% |
| `ema_trend_fast50_slow300` | 9 | 8.1% | -2.8% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 7 | 11.4% | -1.8% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 80/80 runs (mean holdout 31.0%, worst 24.7%, mean DSR 0.458)
- KEEP: `sma_trend_period200` was positive in 80/80 runs (mean holdout 29.9%, worst 21.4%, mean DSR 0.165)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 80/80 runs (mean holdout 29.0%, worst 21.2%, mean DSR 0.475)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 80/80 runs (mean holdout 28.5%, worst 22.9%, mean DSR 0.195)
- KEEP: `sma_trend_period175` was positive in 80/80 runs (mean holdout 27.4%, worst 17.4%, mean DSR 0.128)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.2%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.7%) - add more parameters to it


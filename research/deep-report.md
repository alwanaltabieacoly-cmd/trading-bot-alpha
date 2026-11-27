# Deep research report

- Runs analysed: **141**
- Candidates per run: ~142
- Cumulative candidates evaluated: **19,698**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-27 23:36:52+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3754** (min 0.1793, max 0.612, over 141 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.7% | -17.1% | 0.168 | 0.226 | 1551 | 0 |
| `sma_trend_vol_filter` | 16.2% | 16.1% | -10.0% | 0.155 | 0.607 | 4595 | 0 |
| `sma_trend_efficiency` | 12.6% | 13.5% | -14.3% | 0.279 | 0.502 | 2164 | 0 |
| `ema_trend` | 10.1% | 10.6% | -16.7% | 0.116 | 0.155 | 820 | 0 |
| `ema_trend_regime` | 10.1% | 9.9% | -11.1% | 0.078 | 0.243 | 1209 | 0 |
| `sma_trend_fast_slow` | 7.4% | 8.1% | -16.4% | 0.142 | 0.234 | 1453 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.2% | 0.113 | 0.187 | 1521 | 0 |
| `sma_trend_confirm` | 7.1% | 5.8% | -17.0% | 0.102 | 0.182 | 978 | 0 |
| `donchian_trend` | 3.9% | 3.0% | -3.9% | 0.299 | 0.429 | 363 | 0 |
| `donchian_trend_vol_filter` | 2.6% | 2.5% | -2.7% | 0.071 | 0.311 | 296 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 141 | 141 | 30.8% | 24.7% | 0.480 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 141 | 141 | 28.9% | 22.9% | 0.221 | 9.9 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 141 | 141 | 28.1% | 21.2% | 0.493 | 9.2 |
| `sma_trend_period200` | 141 | 141 | 27.9% | 20.5% | 0.171 | 9.3 |
| `sma_trend_period50` | 141 | 141 | 26.3% | 13.2% | 0.201 | 8.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 141 | 141 | 26.2% | 19.6% | 0.492 | 8.5 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 141 | 141 | 25.2% | 17.2% | 0.475 | 9.6 |
| `sma_trend_period175` | 141 | 141 | 24.8% | 16.9% | 0.132 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 141 | 141 | 24.5% | 18.1% | 0.133 | 8.6 |
| `sma_trend_period225` | 141 | 141 | 23.2% | 16.2% | 0.167 | 8.6 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 128 | 6.5% | -3.2% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 89 | 4.9% | -1.8% |
| `sma_trend_slope_period150_slope_bars40` | 86 | 12.0% | -2.6% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 26 | 8.1% | -2.1% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 141/141 runs (mean holdout 30.8%, worst 24.7%, mean DSR 0.480)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 141/141 runs (mean holdout 28.9%, worst 22.9%, mean DSR 0.221)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 141/141 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.493)
- KEEP: `sma_trend_period200` was positive in 141/141 runs (mean holdout 27.9%, worst 20.5%, mean DSR 0.171)
- KEEP: `sma_trend_period50` was positive in 141/141 runs (mean holdout 26.3%, worst 13.2%, mean DSR 0.201)
- FAMILY `sma_trend` has the best median holdout CAGR (19.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (16.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.5%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (10.6%) - add more parameters to it


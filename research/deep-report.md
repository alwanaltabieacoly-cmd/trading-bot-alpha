# Deep research report

- Runs analysed: **89**
- Candidates per run: ~142
- Cumulative candidates evaluated: **12,314**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-11 06:44:52+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4112** (min 0.1793, max 0.612, over 89 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.6% | 20.2% | -17.0% | 0.165 | 0.226 | 979 | 0 |
| `sma_trend_vol_filter` | 15.5% | 14.8% | -10.3% | 0.148 | 0.607 | 2949 | 0 |
| `sma_trend_efficiency` | 12.3% | 12.7% | -14.1% | 0.272 | 0.491 | 1332 | 0 |
| `ema_trend` | 11.2% | 11.8% | -16.0% | 0.114 | 0.155 | 516 | 0 |
| `ema_trend_regime` | 9.7% | 9.6% | -11.3% | 0.073 | 0.241 | 780 | 0 |
| `sma_trend_fast_slow` | 7.3% | 8.3% | -16.4% | 0.139 | 0.228 | 935 | 0 |
| `sma_trend_slope` | 7.9% | 8.0% | -15.1% | 0.111 | 0.184 | 951 | 0 |
| `sma_trend_confirm` | 7.1% | 5.4% | -17.1% | 0.101 | 0.179 | 573 | 0 |
| `donchian_trend` | 3.0% | 2.1% | -4.0% | 0.299 | 0.429 | 207 | 0 |
| `donchian_trend_vol_filter` | 1.9% | 1.3% | -2.8% | 0.074 | 0.311 | 192 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 89 | 89 | 30.6% | 24.7% | 0.463 | 8.8 |
| `sma_trend_period200` | 89 | 89 | 29.1% | 20.7% | 0.166 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 89 | 89 | 28.4% | 21.2% | 0.479 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 89 | 89 | 28.2% | 22.9% | 0.200 | 9.8 |
| `sma_trend_period175` | 89 | 89 | 26.5% | 17.1% | 0.129 | 9.3 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 89 | 89 | 26.1% | 19.6% | 0.474 | 8.8 |
| `sma_trend_period50` | 89 | 89 | 26.0% | 13.2% | 0.200 | 8.7 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 89 | 89 | 25.2% | 17.2% | 0.461 | 9.9 |
| `sma_trend_period225` | 89 | 89 | 24.4% | 16.2% | 0.162 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 89 | 89 | 24.0% | 18.1% | 0.117 | 8.9 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 76 | 6.6% | -3.7% |
| `sma_trend_confirm_slow_period100_fast_period50` | 48 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 37 | 5.1% | -2.9% |
| `sma_trend_slope_period150_slope_bars40` | 34 | 12.5% | -3.6% |
| `sma_trend_confirm_slow_period100_fast_period20` | 32 | 9.8% | -1.4% |
| `sma_trend_slope_period100_slope_bars10` | 31 | 12.7% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 24 | 11.9% | -0.9% |
| `ema_trend_fast50_slow300` | 18 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 12 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 89/89 runs (mean holdout 30.6%, worst 24.7%, mean DSR 0.463)
- KEEP: `sma_trend_period200` was positive in 89/89 runs (mean holdout 29.1%, worst 20.7%, mean DSR 0.166)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 89/89 runs (mean holdout 28.4%, worst 21.2%, mean DSR 0.479)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 89/89 runs (mean holdout 28.2%, worst 22.9%, mean DSR 0.200)
- KEEP: `sma_trend_period175` was positive in 89/89 runs (mean holdout 26.5%, worst 17.1%, mean DSR 0.129)
- FAMILY `sma_trend` has the best median holdout CAGR (20.2%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.8%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.8%) - add more parameters to it


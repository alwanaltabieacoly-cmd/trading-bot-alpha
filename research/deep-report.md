# Deep research report

- Runs analysed: **86**
- Candidates per run: ~142
- Cumulative candidates evaluated: **11,888**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-10 10:05:09+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4159** (min 0.1793, max 0.612, over 86 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.9% | 20.3% | -16.9% | 0.165 | 0.226 | 946 | 0 |
| `sma_trend_vol_filter` | 15.6% | 14.9% | -10.4% | 0.147 | 0.607 | 2849 | 0 |
| `sma_trend_efficiency` | 12.4% | 12.7% | -14.1% | 0.272 | 0.489 | 1284 | 0 |
| `ema_trend` | 11.4% | 12.1% | -16.0% | 0.114 | 0.155 | 501 | 0 |
| `ema_trend_regime` | 9.8% | 9.7% | -11.3% | 0.073 | 0.241 | 753 | 0 |
| `sma_trend_fast_slow` | 7.4% | 8.4% | -16.4% | 0.138 | 0.227 | 906 | 0 |
| `sma_trend_slope` | 8.0% | 8.3% | -15.0% | 0.111 | 0.183 | 919 | 0 |
| `sma_trend_confirm` | 7.2% | 5.5% | -17.1% | 0.101 | 0.178 | 555 | 0 |
| `donchian_trend` | 2.9% | 2.1% | -4.0% | 0.299 | 0.429 | 198 | 0 |
| `donchian_trend_vol_filter` | 1.8% | 1.2% | -2.9% | 0.075 | 0.311 | 186 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 86 | 86 | 30.7% | 24.7% | 0.461 | 8.8 |
| `sma_trend_period200` | 86 | 86 | 29.4% | 21.4% | 0.166 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 86 | 86 | 28.6% | 21.2% | 0.477 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 86 | 86 | 28.3% | 22.9% | 0.199 | 9.8 |
| `sma_trend_period175` | 86 | 86 | 26.8% | 17.4% | 0.128 | 9.3 |
| `sma_trend_period50` | 86 | 86 | 26.2% | 13.2% | 0.200 | 8.8 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 86 | 86 | 26.2% | 19.6% | 0.473 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 86 | 86 | 25.3% | 17.2% | 0.458 | 10.0 |
| `sma_trend_period225` | 86 | 86 | 24.7% | 16.2% | 0.162 | 9.5 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 86 | 86 | 24.0% | 18.1% | 0.116 | 8.9 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 73 | 6.6% | -3.6% |
| `sma_trend_confirm_slow_period100_fast_period50` | 45 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 34 | 5.1% | -2.9% |
| `sma_trend_slope_period150_slope_bars40` | 31 | 12.5% | -3.5% |
| `sma_trend_confirm_slow_period100_fast_period20` | 31 | 9.9% | -1.4% |
| `sma_trend_slope_period100_slope_bars10` | 30 | 12.8% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 23 | 12.0% | -0.9% |
| `ema_trend_fast50_slow300` | 15 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 11 | 11.5% | -1.3% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 86/86 runs (mean holdout 30.7%, worst 24.7%, mean DSR 0.461)
- KEEP: `sma_trend_period200` was positive in 86/86 runs (mean holdout 29.4%, worst 21.4%, mean DSR 0.166)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 86/86 runs (mean holdout 28.6%, worst 21.2%, mean DSR 0.477)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 86/86 runs (mean holdout 28.3%, worst 22.9%, mean DSR 0.199)
- KEEP: `sma_trend_period175` was positive in 86/86 runs (mean holdout 26.8%, worst 17.4%, mean DSR 0.128)
- FAMILY `sma_trend` has the best median holdout CAGR (20.3%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.9%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.1%) - add more parameters to it


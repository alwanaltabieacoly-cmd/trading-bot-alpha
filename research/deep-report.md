# Deep research report

- Runs analysed: **78**
- Candidates per run: ~142
- Cumulative candidates evaluated: **10,752**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-07 22:01:02+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4299** (min 0.1793, max 0.612, over 78 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.6% | 20.7% | -16.9% | 0.164 | 0.213 | 858 | 0 |
| `sma_trend_vol_filter` | 15.9% | 15.3% | -10.4% | 0.145 | 0.600 | 2577 | 0 |
| `ema_trend` | 11.9% | 12.8% | -15.9% | 0.113 | 0.155 | 461 | 0 |
| `sma_trend_efficiency` | 12.5% | 12.7% | -14.0% | 0.270 | 0.488 | 1156 | 0 |
| `ema_trend_regime` | 10.1% | 10.0% | -11.3% | 0.071 | 0.231 | 675 | 0 |
| `sma_trend_slope` | 8.5% | 9.0% | -15.0% | 0.110 | 0.183 | 843 | 0 |
| `sma_trend_fast_slow` | 7.9% | 8.9% | -16.3% | 0.137 | 0.226 | 835 | 0 |
| `sma_trend_confirm` | 7.7% | 5.9% | -17.0% | 0.100 | 0.178 | 515 | 0 |
| `donchian_trend` | 2.8% | 2.0% | -4.1% | 0.300 | 0.429 | 174 | 0 |
| `donchian_trend_vol_filter` | 1.7% | 1.2% | -2.9% | 0.076 | 0.311 | 167 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 78 | 78 | 31.1% | 24.7% | 0.457 | 8.8 |
| `sma_trend_period200` | 78 | 78 | 30.1% | 21.4% | 0.165 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 78 | 78 | 29.1% | 21.2% | 0.473 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 78 | 78 | 28.6% | 22.9% | 0.194 | 9.8 |
| `sma_trend_period175` | 78 | 78 | 27.7% | 17.4% | 0.128 | 9.3 |
| `sma_trend_period50` | 78 | 78 | 27.2% | 13.2% | 0.197 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 78 | 78 | 26.6% | 19.6% | 0.469 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 78 | 78 | 26.0% | 17.3% | 0.451 | 10.2 |
| `sma_trend_period225` | 78 | 78 | 25.4% | 16.2% | 0.161 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 78 | 78 | 24.4% | 18.1% | 0.113 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 65 | 6.6% | -3.3% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 37 | 9.9% | -1.4% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 26 | 5.0% | -2.6% |
| `sma_trend_confirm_slow_period100_fast_period20` | 25 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 24 | 12.9% | -1.4% |
| `sma_trend_slope_period150_slope_bars40` | 23 | 12.6% | -3.3% |
| `sma_trend_confirm_slow_period150_fast_period50` | 18 | 12.2% | -0.9% |
| `ema_trend_fast50_slow300` | 7 | 8.1% | -2.6% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 5 | 11.3% | -1.8% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 78/78 runs (mean holdout 31.1%, worst 24.7%, mean DSR 0.457)
- KEEP: `sma_trend_period200` was positive in 78/78 runs (mean holdout 30.1%, worst 21.4%, mean DSR 0.165)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 78/78 runs (mean holdout 29.1%, worst 21.2%, mean DSR 0.473)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 78/78 runs (mean holdout 28.6%, worst 22.9%, mean DSR 0.194)
- KEEP: `sma_trend_period175` was positive in 78/78 runs (mean holdout 27.7%, worst 17.4%, mean DSR 0.128)
- FAMILY `sma_trend` has the best median holdout CAGR (20.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.8%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it


# Deep research report

- Runs analysed: **77**
- Candidates per run: ~142
- Cumulative candidates evaluated: **10,610**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-07 18:09:09+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4322** (min 0.1793, max 0.612, over 77 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.7% | 20.7% | -16.8% | 0.163 | 0.213 | 847 | 0 |
| `sma_trend_vol_filter` | 16.0% | 15.3% | -10.4% | 0.145 | 0.600 | 2546 | 0 |
| `ema_trend` | 12.0% | 12.9% | -15.9% | 0.113 | 0.155 | 456 | 0 |
| `sma_trend_efficiency` | 12.5% | 12.7% | -14.0% | 0.270 | 0.488 | 1140 | 0 |
| `ema_trend_regime` | 10.2% | 10.0% | -11.3% | 0.071 | 0.231 | 667 | 0 |
| `sma_trend_slope` | 8.6% | 9.2% | -14.9% | 0.110 | 0.183 | 835 | 0 |
| `sma_trend_fast_slow` | 8.0% | 9.0% | -16.3% | 0.137 | 0.226 | 827 | 0 |
| `sma_trend_confirm` | 7.8% | 5.9% | -17.0% | 0.100 | 0.178 | 511 | 0 |
| `donchian_trend` | 2.7% | 2.0% | -4.1% | 0.300 | 0.429 | 171 | 0 |
| `donchian_trend_vol_filter` | 1.7% | 1.2% | -2.9% | 0.076 | 0.311 | 165 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 77 | 77 | 31.2% | 24.7% | 0.457 | 8.8 |
| `sma_trend_period200` | 77 | 77 | 30.2% | 21.4% | 0.164 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 77 | 77 | 29.2% | 21.2% | 0.473 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 77 | 77 | 28.7% | 22.9% | 0.194 | 9.8 |
| `sma_trend_period175` | 77 | 77 | 27.8% | 17.4% | 0.127 | 9.4 |
| `sma_trend_period50` | 77 | 77 | 27.3% | 13.2% | 0.197 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 77 | 77 | 26.7% | 19.6% | 0.468 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 77 | 77 | 26.1% | 17.3% | 0.450 | 10.2 |
| `sma_trend_period225` | 77 | 77 | 25.5% | 16.2% | 0.161 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 77 | 77 | 24.5% | 18.1% | 0.113 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 64 | 6.6% | -3.3% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 36 | 9.9% | -1.3% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 25 | 5.0% | -2.5% |
| `sma_trend_confirm_slow_period100_fast_period20` | 24 | 9.9% | -1.2% |
| `sma_trend_slope_period100_slope_bars10` | 23 | 12.9% | -1.3% |
| `sma_trend_slope_period150_slope_bars40` | 22 | 12.6% | -3.2% |
| `sma_trend_confirm_slow_period150_fast_period50` | 17 | 12.2% | -0.8% |
| `ema_trend_fast50_slow300` | 6 | 8.1% | -2.5% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 4 | 11.3% | -1.8% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 77/77 runs (mean holdout 31.2%, worst 24.7%, mean DSR 0.457)
- KEEP: `sma_trend_period200` was positive in 77/77 runs (mean holdout 30.2%, worst 21.4%, mean DSR 0.164)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 77/77 runs (mean holdout 29.2%, worst 21.2%, mean DSR 0.473)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 77/77 runs (mean holdout 28.7%, worst 22.9%, mean DSR 0.194)
- KEEP: `sma_trend_period175` was positive in 77/77 runs (mean holdout 27.8%, worst 17.4%, mean DSR 0.127)
- FAMILY `sma_trend` has the best median holdout CAGR (20.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.9%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it


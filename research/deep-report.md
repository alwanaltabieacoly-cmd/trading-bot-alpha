# Deep research report

- Runs analysed: **107**
- Candidates per run: ~142
- Cumulative candidates evaluated: **14,870**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-16 02:53:21+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3958** (min 0.1793, max 0.612, over 107 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.7% | -17.0% | 0.166 | 0.226 | 1177 | 0 |
| `sma_trend_vol_filter` | 15.6% | 15.3% | -10.2% | 0.151 | 0.607 | 3538 | 0 |
| `sma_trend_efficiency` | 12.4% | 13.1% | -14.2% | 0.275 | 0.493 | 1620 | 0 |
| `ema_trend` | 10.6% | 11.0% | -16.3% | 0.114 | 0.155 | 619 | 0 |
| `ema_trend_regime` | 9.8% | 9.7% | -11.2% | 0.075 | 0.243 | 937 | 0 |
| `sma_trend_fast_slow` | 7.2% | 8.1% | -16.4% | 0.140 | 0.229 | 1113 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.2% | 0.112 | 0.184 | 1147 | 0 |
| `sma_trend_confirm` | 6.9% | 5.3% | -17.1% | 0.101 | 0.179 | 706 | 0 |
| `donchian_trend` | 3.4% | 2.4% | -4.0% | 0.299 | 0.429 | 261 | 0 |
| `donchian_trend_vol_filter` | 2.2% | 1.8% | -2.8% | 0.073 | 0.311 | 228 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 107 | 107 | 30.5% | 24.7% | 0.470 | 8.8 |
| `sma_trend_period200` | 107 | 107 | 28.4% | 20.5% | 0.168 | 9.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 107 | 107 | 28.3% | 22.9% | 0.209 | 9.8 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 107 | 107 | 28.1% | 21.2% | 0.484 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 107 | 107 | 26.0% | 19.6% | 0.481 | 8.7 |
| `sma_trend_period50` | 107 | 107 | 25.8% | 13.2% | 0.202 | 8.7 |
| `sma_trend_period175` | 107 | 107 | 25.6% | 16.9% | 0.130 | 9.3 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 107 | 107 | 24.9% | 17.2% | 0.470 | 9.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 107 | 107 | 24.0% | 18.1% | 0.123 | 8.7 |
| `sma_trend_period225` | 107 | 107 | 23.8% | 16.2% | 0.164 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 94 | 6.6% | -3.5% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 55 | 5.0% | -2.3% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_slope_period150_slope_bars40` | 52 | 12.2% | -3.2% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 107/107 runs (mean holdout 30.5%, worst 24.7%, mean DSR 0.470)
- KEEP: `sma_trend_period200` was positive in 107/107 runs (mean holdout 28.4%, worst 20.5%, mean DSR 0.168)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 107/107 runs (mean holdout 28.3%, worst 22.9%, mean DSR 0.209)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 107/107 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.484)
- KEEP: `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` was positive in 107/107 runs (mean holdout 26.0%, worst 19.6%, mean DSR 0.481)
- FAMILY `sma_trend` has the best median holdout CAGR (19.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.3%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.1%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.0%) - add more parameters to it


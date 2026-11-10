# Deep research report

- Runs analysed: **88**
- Candidates per run: ~142
- Cumulative candidates evaluated: **12,172**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-10 23:32:30+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4132** (min 0.1793, max 0.612, over 88 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.7% | 20.3% | -16.9% | 0.165 | 0.226 | 968 | 0 |
| `sma_trend_vol_filter` | 15.5% | 14.9% | -10.4% | 0.147 | 0.607 | 2917 | 0 |
| `sma_trend_efficiency` | 12.3% | 12.7% | -14.1% | 0.272 | 0.489 | 1316 | 0 |
| `ema_trend` | 11.2% | 11.9% | -16.0% | 0.114 | 0.155 | 511 | 0 |
| `ema_trend_regime` | 9.7% | 9.7% | -11.3% | 0.073 | 0.241 | 771 | 0 |
| `sma_trend_fast_slow` | 7.4% | 8.4% | -16.4% | 0.138 | 0.227 | 926 | 0 |
| `sma_trend_slope` | 7.9% | 8.1% | -15.1% | 0.111 | 0.183 | 941 | 0 |
| `sma_trend_confirm` | 7.1% | 5.4% | -17.1% | 0.101 | 0.178 | 569 | 0 |
| `donchian_trend` | 3.0% | 2.1% | -4.0% | 0.299 | 0.429 | 204 | 0 |
| `donchian_trend_vol_filter` | 1.9% | 1.3% | -2.8% | 0.075 | 0.311 | 190 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 88 | 88 | 30.6% | 24.7% | 0.462 | 8.8 |
| `sma_trend_period200` | 88 | 88 | 29.2% | 21.4% | 0.166 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 88 | 88 | 28.5% | 21.2% | 0.478 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 88 | 88 | 28.2% | 22.9% | 0.200 | 9.8 |
| `sma_trend_period175` | 88 | 88 | 26.6% | 17.4% | 0.129 | 9.3 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 88 | 88 | 26.1% | 19.6% | 0.474 | 8.8 |
| `sma_trend_period50` | 88 | 88 | 26.1% | 13.2% | 0.200 | 8.7 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 88 | 88 | 25.2% | 17.2% | 0.460 | 9.9 |
| `sma_trend_period225` | 88 | 88 | 24.5% | 16.2% | 0.162 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 88 | 88 | 24.0% | 18.1% | 0.117 | 8.9 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 75 | 6.6% | -3.7% |
| `sma_trend_confirm_slow_period100_fast_period50` | 47 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 36 | 5.1% | -2.9% |
| `sma_trend_slope_period150_slope_bars40` | 33 | 12.5% | -3.5% |
| `sma_trend_confirm_slow_period100_fast_period20` | 31 | 9.9% | -1.4% |
| `sma_trend_slope_period100_slope_bars10` | 30 | 12.8% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 23 | 12.0% | -0.9% |
| `ema_trend_fast50_slow300` | 17 | 8.2% | -2.3% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 11 | 11.5% | -1.3% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 88/88 runs (mean holdout 30.6%, worst 24.7%, mean DSR 0.462)
- KEEP: `sma_trend_period200` was positive in 88/88 runs (mean holdout 29.2%, worst 21.4%, mean DSR 0.166)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 88/88 runs (mean holdout 28.5%, worst 21.2%, mean DSR 0.478)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 88/88 runs (mean holdout 28.2%, worst 22.9%, mean DSR 0.200)
- KEEP: `sma_trend_period175` was positive in 88/88 runs (mean holdout 26.6%, worst 17.4%, mean DSR 0.129)
- FAMILY `sma_trend` has the best median holdout CAGR (20.3%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.9%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.9%) - add more parameters to it


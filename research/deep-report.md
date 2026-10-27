# Deep research report

- Runs analysed: **34**
- Candidates per run: ~142
- Cumulative candidates evaluated: **4,504**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-27 16:46:45+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4174** (min 0.1793, max 0.612, over 34 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.2% | 21.9% | -16.4% | 0.156 | 0.203 | 374 | 0 |
| `sma_trend_vol_filter` | 15.4% | 14.7% | -10.4% | 0.131 | 0.569 | 1135 | 0 |
| `ema_trend` | 12.8% | 12.9% | -15.2% | 0.110 | 0.155 | 204 | 0 |
| `sma_trend_efficiency` | 13.0% | 12.4% | -13.8% | 0.255 | 0.478 | 465 | 0 |
| `sma_trend_slope` | 9.0% | 9.8% | -14.3% | 0.105 | 0.177 | 347 | 0 |
| `ema_trend_regime` | 9.9% | 9.8% | -11.1% | 0.063 | 0.187 | 284 | 0 |
| `sma_trend_fast_slow` | 7.5% | 9.0% | -16.3% | 0.129 | 0.217 | 358 | 0 |
| `sma_trend_confirm` | 8.1% | 5.8% | -16.5% | 0.095 | 0.172 | 220 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.302 | 0.429 | 68 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.084 | 0.311 | 68 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 34 | 34 | 30.9% | 28.1% | 0.153 | 9.6 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 34 | 34 | 30.7% | 27.4% | 0.419 | 8.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 34 | 34 | 28.5% | 25.5% | 0.441 | 7.7 |
| `sma_trend_period50` | 34 | 34 | 28.4% | 25.4% | 0.193 | 8.6 |
| `sma_trend_period175` | 34 | 34 | 28.3% | 25.7% | 0.119 | 8.6 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 34 | 34 | 27.9% | 25.0% | 0.155 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 34 | 34 | 26.2% | 24.5% | 0.428 | 10.5 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 34 | 34 | 26.2% | 22.7% | 0.432 | 8.6 |
| `sma_trend_period225` | 34 | 34 | 26.2% | 23.1% | 0.150 | 9.6 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 31 | 31 | 23.8% | 21.3% | 0.187 | 9.6 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 31 | 6.8% | -1.4% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 31 | 6.9% | -4.5% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 34/34 runs (mean holdout 30.9%, worst 28.1%, mean DSR 0.153)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 34/34 runs (mean holdout 30.7%, worst 27.4%, mean DSR 0.419)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 34/34 runs (mean holdout 28.5%, worst 25.5%, mean DSR 0.441)
- KEEP: `sma_trend_period50` was positive in 34/34 runs (mean holdout 28.4%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_period175` was positive in 34/34 runs (mean holdout 28.3%, worst 25.7%, mean DSR 0.119)
- FAMILY `sma_trend` has the best median holdout CAGR (21.9%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.9%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.4%) - add more parameters to it


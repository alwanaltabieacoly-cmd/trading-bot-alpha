# Deep research report

- Runs analysed: **46**
- Candidates per run: ~142
- Cumulative candidates evaluated: **6,208**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-30 14:24:14+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4404** (min 0.1793, max 0.612, over 46 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 22.0% | 22.6% | -16.5% | 0.158 | 0.203 | 506 | 0 |
| `sma_trend_vol_filter` | 16.2% | 15.5% | -10.4% | 0.136 | 0.578 | 1531 | 0 |
| `ema_trend` | 13.3% | 14.0% | -15.4% | 0.111 | 0.155 | 276 | 0 |
| `sma_trend_efficiency` | 13.0% | 13.9% | -13.8% | 0.262 | 0.478 | 646 | 0 |
| `sma_trend_slope` | 9.7% | 10.7% | -14.4% | 0.107 | 0.179 | 491 | 0 |
| `ema_trend_regime` | 10.7% | 10.5% | -11.2% | 0.065 | 0.200 | 392 | 0 |
| `sma_trend_fast_slow` | 8.3% | 9.4% | -16.3% | 0.132 | 0.221 | 495 | 0 |
| `sma_trend_confirm` | 8.8% | 6.9% | -16.6% | 0.097 | 0.174 | 315 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.301 | 0.429 | 92 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.080 | 0.311 | 92 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 46 | 46 | 31.7% | 27.4% | 0.434 | 8.7 |
| `sma_trend_period200` | 46 | 46 | 31.7% | 28.1% | 0.158 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 46 | 46 | 29.6% | 25.5% | 0.454 | 8.3 |
| `sma_trend_period50` | 46 | 46 | 29.2% | 25.4% | 0.193 | 8.8 |
| `sma_trend_period175` | 46 | 46 | 29.1% | 25.7% | 0.123 | 9.0 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 46 | 46 | 29.0% | 25.0% | 0.170 | 9.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 46 | 46 | 27.3% | 22.7% | 0.446 | 8.7 |
| `sma_trend_period225` | 46 | 46 | 27.1% | 23.1% | 0.154 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 46 | 46 | 26.8% | 24.5% | 0.433 | 10.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 46 | 46 | 25.0% | 20.7% | 0.096 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 42 | 6.8% | -1.2% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 38 | 6.7% | -3.7% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 5 | 10.6% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 46/46 runs (mean holdout 31.7%, worst 27.4%, mean DSR 0.434)
- KEEP: `sma_trend_period200` was positive in 46/46 runs (mean holdout 31.7%, worst 28.1%, mean DSR 0.158)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 46/46 runs (mean holdout 29.6%, worst 25.5%, mean DSR 0.454)
- KEEP: `sma_trend_period50` was positive in 46/46 runs (mean holdout 29.2%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_period175` was positive in 46/46 runs (mean holdout 29.1%, worst 25.7%, mean DSR 0.123)
- FAMILY `sma_trend` has the best median holdout CAGR (22.6%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.5%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (14.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.9%) - add more parameters to it


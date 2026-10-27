# Deep research report

- Runs analysed: **32**
- Candidates per run: ~142
- Cumulative candidates evaluated: **4,220**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-27 05:18:02+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4108** (min 0.1793, max 0.612, over 32 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.0% | 21.4% | -16.4% | 0.155 | 0.203 | 352 | 0 |
| `sma_trend_vol_filter` | 15.2% | 14.6% | -10.4% | 0.130 | 0.569 | 1069 | 0 |
| `sma_trend_efficiency` | 13.0% | 12.4% | -13.7% | 0.254 | 0.478 | 435 | 0 |
| `ema_trend` | 12.5% | 12.4% | -15.2% | 0.110 | 0.155 | 192 | 0 |
| `sma_trend_slope` | 8.8% | 9.8% | -14.3% | 0.105 | 0.177 | 323 | 0 |
| `ema_trend_regime` | 9.7% | 9.5% | -11.1% | 0.062 | 0.187 | 266 | 0 |
| `sma_trend_fast_slow` | 7.3% | 8.9% | -16.3% | 0.128 | 0.217 | 334 | 0 |
| `sma_trend_confirm` | 7.8% | 5.8% | -16.5% | 0.095 | 0.172 | 204 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.302 | 0.429 | 64 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.084 | 0.311 | 64 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 32 | 32 | 30.6% | 28.1% | 0.152 | 9.5 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 32 | 32 | 30.3% | 27.4% | 0.416 | 8.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 32 | 32 | 28.2% | 25.5% | 0.439 | 7.6 |
| `sma_trend_period50` | 32 | 32 | 28.1% | 25.4% | 0.193 | 8.6 |
| `sma_trend_period175` | 32 | 32 | 28.1% | 25.7% | 0.118 | 8.6 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 32 | 32 | 27.6% | 25.0% | 0.152 | 9.5 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 32 | 32 | 26.1% | 24.5% | 0.427 | 10.5 |
| `sma_trend_period225` | 32 | 32 | 25.9% | 23.1% | 0.149 | 9.5 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 32 | 32 | 25.9% | 22.7% | 0.428 | 8.5 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 29 | 29 | 23.9% | 21.3% | 0.185 | 9.6 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 31 | 6.9% | -4.5% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 29 | 6.8% | -1.5% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 32/32 runs (mean holdout 30.6%, worst 28.1%, mean DSR 0.152)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 32/32 runs (mean holdout 30.3%, worst 27.4%, mean DSR 0.416)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 32/32 runs (mean holdout 28.2%, worst 25.5%, mean DSR 0.439)
- KEEP: `sma_trend_period50` was positive in 32/32 runs (mean holdout 28.1%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_period175` was positive in 32/32 runs (mean holdout 28.1%, worst 25.7%, mean DSR 0.118)
- FAMILY `sma_trend` has the best median holdout CAGR (21.4%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.6%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.4%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.4%) - add more parameters to it


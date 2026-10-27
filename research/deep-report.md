# Deep research report

- Runs analysed: **35**
- Candidates per run: ~142
- Cumulative candidates evaluated: **4,646**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-27 21:26:08+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4204** (min 0.1793, max 0.612, over 35 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.4% | 21.9% | -16.4% | 0.156 | 0.203 | 385 | 0 |
| `sma_trend_vol_filter` | 15.5% | 14.8% | -10.4% | 0.132 | 0.569 | 1168 | 0 |
| `ema_trend` | 12.9% | 13.0% | -15.3% | 0.110 | 0.155 | 210 | 0 |
| `sma_trend_efficiency` | 13.0% | 12.4% | -13.8% | 0.256 | 0.478 | 480 | 0 |
| `sma_trend_slope` | 9.2% | 9.9% | -14.3% | 0.105 | 0.177 | 359 | 0 |
| `ema_trend_regime` | 10.1% | 9.8% | -11.1% | 0.063 | 0.187 | 293 | 0 |
| `sma_trend_fast_slow` | 7.6% | 9.0% | -16.3% | 0.129 | 0.217 | 370 | 0 |
| `sma_trend_confirm` | 8.2% | 5.8% | -16.5% | 0.096 | 0.172 | 228 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.302 | 0.429 | 70 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.083 | 0.311 | 70 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 35 | 35 | 31.0% | 28.1% | 0.154 | 9.6 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 35 | 35 | 30.8% | 27.4% | 0.421 | 8.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 35 | 35 | 28.7% | 25.5% | 0.443 | 7.8 |
| `sma_trend_period50` | 35 | 35 | 28.6% | 25.4% | 0.193 | 8.7 |
| `sma_trend_period175` | 35 | 35 | 28.4% | 25.7% | 0.120 | 8.7 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 35 | 35 | 28.1% | 25.0% | 0.157 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 35 | 35 | 26.4% | 22.7% | 0.433 | 8.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 35 | 35 | 26.3% | 24.5% | 0.428 | 10.5 |
| `sma_trend_period225` | 35 | 35 | 26.3% | 23.1% | 0.150 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 35 | 35 | 24.0% | 20.7% | 0.087 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 32 | 6.8% | -1.4% |
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

- KEEP: `sma_trend_period200` was positive in 35/35 runs (mean holdout 31.0%, worst 28.1%, mean DSR 0.154)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 35/35 runs (mean holdout 30.8%, worst 27.4%, mean DSR 0.421)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 35/35 runs (mean holdout 28.7%, worst 25.5%, mean DSR 0.443)
- KEEP: `sma_trend_period50` was positive in 35/35 runs (mean holdout 28.6%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_period175` was positive in 35/35 runs (mean holdout 28.4%, worst 25.7%, mean DSR 0.120)
- FAMILY `sma_trend` has the best median holdout CAGR (21.9%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.8%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.4%) - add more parameters to it


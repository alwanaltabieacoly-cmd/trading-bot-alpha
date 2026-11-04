# Deep research report

- Runs analysed: **64**
- Candidates per run: ~142
- Cumulative candidates evaluated: **8,764**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-04 02:28:29+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4421** (min 0.1793, max 0.612, over 64 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.6% | 21.6% | -16.7% | 0.162 | 0.210 | 704 | 0 |
| `sma_trend_vol_filter` | 16.4% | 15.7% | -10.4% | 0.141 | 0.596 | 2120 | 0 |
| `ema_trend` | 12.8% | 13.4% | -15.7% | 0.112 | 0.155 | 384 | 0 |
| `sma_trend_efficiency` | 12.7% | 12.8% | -14.0% | 0.267 | 0.483 | 932 | 0 |
| `ema_trend_regime` | 10.6% | 10.6% | -11.3% | 0.069 | 0.227 | 554 | 0 |
| `sma_trend_slope` | 9.2% | 9.9% | -14.7% | 0.109 | 0.181 | 700 | 0 |
| `sma_trend_fast_slow` | 8.5% | 9.7% | -16.3% | 0.135 | 0.224 | 698 | 0 |
| `sma_trend_confirm` | 8.3% | 6.4% | -16.9% | 0.099 | 0.176 | 435 | 0 |
| `donchian_trend` | 2.6% | 2.0% | -4.1% | 0.300 | 0.429 | 132 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 1.1% | -3.0% | 0.077 | 0.311 | 139 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 64 | 64 | 31.7% | 27.4% | 0.449 | 8.8 |
| `sma_trend_period200` | 64 | 64 | 31.1% | 25.7% | 0.162 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 64 | 64 | 29.8% | 25.5% | 0.466 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 64 | 64 | 29.2% | 25.0% | 0.185 | 9.8 |
| `sma_trend_period50` | 64 | 64 | 28.8% | 22.9% | 0.195 | 8.9 |
| `sma_trend_period175` | 64 | 64 | 28.7% | 23.8% | 0.126 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 64 | 64 | 27.4% | 22.7% | 0.460 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 64 | 64 | 26.7% | 23.7% | 0.443 | 10.4 |
| `sma_trend_period225` | 64 | 64 | 26.5% | 21.0% | 0.158 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 64 | 64 | 25.1% | 20.7% | 0.106 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 51 | 6.6% | -3.1% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 23 | 9.9% | -0.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_confirm_slow_period100_fast_period20` | 18 | 10.0% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 17 | 13.2% | -1.2% |
| `sma_trend_slope_period150_slope_bars40` | 15 | 12.9% | -3.0% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 64/64 runs (mean holdout 31.7%, worst 27.4%, mean DSR 0.449)
- KEEP: `sma_trend_period200` was positive in 64/64 runs (mean holdout 31.1%, worst 25.7%, mean DSR 0.162)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 64/64 runs (mean holdout 29.8%, worst 25.5%, mean DSR 0.466)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 64/64 runs (mean holdout 29.2%, worst 25.0%, mean DSR 0.185)
- KEEP: `sma_trend_period50` was positive in 64/64 runs (mean holdout 28.8%, worst 22.9%, mean DSR 0.195)
- FAMILY `sma_trend` has the best median holdout CAGR (21.6%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.4%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.8%) - add more parameters to it


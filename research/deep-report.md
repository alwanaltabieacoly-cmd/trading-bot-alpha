# Deep research report

- Runs analysed: **69**
- Candidates per run: ~142
- Cumulative candidates evaluated: **9,474**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-05 16:35:19+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4433** (min 0.1793, max 0.612, over 69 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.5% | 21.4% | -16.7% | 0.162 | 0.210 | 759 | 0 |
| `sma_trend_vol_filter` | 16.4% | 15.7% | -10.4% | 0.143 | 0.596 | 2287 | 0 |
| `ema_trend` | 12.6% | 13.3% | -15.8% | 0.113 | 0.155 | 414 | 0 |
| `sma_trend_efficiency` | 12.7% | 13.0% | -14.0% | 0.268 | 0.483 | 1012 | 0 |
| `ema_trend_regime` | 10.6% | 10.6% | -11.3% | 0.070 | 0.227 | 599 | 0 |
| `sma_trend_slope` | 9.1% | 9.8% | -14.8% | 0.110 | 0.181 | 759 | 0 |
| `sma_trend_fast_slow` | 8.5% | 9.7% | -16.3% | 0.136 | 0.224 | 753 | 0 |
| `sma_trend_confirm` | 8.3% | 6.4% | -16.9% | 0.099 | 0.176 | 470 | 0 |
| `donchian_trend` | 2.6% | 2.0% | -4.1% | 0.300 | 0.429 | 147 | 0 |
| `donchian_trend_vol_filter` | 1.6% | 1.1% | -2.9% | 0.077 | 0.311 | 149 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 69 | 69 | 31.7% | 27.4% | 0.452 | 8.8 |
| `sma_trend_period200` | 69 | 69 | 30.9% | 25.7% | 0.163 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 69 | 69 | 29.8% | 25.5% | 0.469 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 69 | 69 | 29.1% | 25.0% | 0.188 | 9.8 |
| `sma_trend_period175` | 69 | 69 | 28.6% | 23.8% | 0.126 | 9.4 |
| `sma_trend_period50` | 69 | 69 | 28.5% | 22.9% | 0.195 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 69 | 69 | 27.3% | 22.7% | 0.464 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 69 | 69 | 26.7% | 23.7% | 0.446 | 10.4 |
| `sma_trend_period225` | 69 | 69 | 26.3% | 21.0% | 0.159 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 69 | 69 | 25.0% | 20.7% | 0.109 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 56 | 6.6% | -3.0% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 28 | 9.9% | -0.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_confirm_slow_period100_fast_period20` | 18 | 10.0% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 17 | 13.2% | -1.2% |
| `sma_trend_slope_period150_slope_bars40` | 16 | 12.9% | -2.9% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 69/69 runs (mean holdout 31.7%, worst 27.4%, mean DSR 0.452)
- KEEP: `sma_trend_period200` was positive in 69/69 runs (mean holdout 30.9%, worst 25.7%, mean DSR 0.163)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 69/69 runs (mean holdout 29.8%, worst 25.5%, mean DSR 0.469)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 69/69 runs (mean holdout 29.1%, worst 25.0%, mean DSR 0.188)
- KEEP: `sma_trend_period175` was positive in 69/69 runs (mean holdout 28.6%, worst 23.8%, mean DSR 0.126)
- FAMILY `sma_trend` has the best median holdout CAGR (21.4%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.3%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.0%) - add more parameters to it


# Deep research report

- Runs analysed: **21**
- Candidates per run: ~124
- Cumulative candidates evaluated: **2,658**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-24 07:24:56+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3421** (min 0.1793, max 0.612, over 21 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.9% | 20.5% | -16.4% | 0.149 | 0.202 | 231 | 0 |
| `sma_trend_vol_filter` | 14.5% | 14.1% | -10.4% | 0.121 | 0.569 | 699 | 0 |
| `sma_trend_efficiency` | 13.2% | 12.3% | -13.7% | 0.239 | 0.478 | 270 | 0 |
| `ema_trend` | 11.4% | 12.1% | -15.1% | 0.109 | 0.155 | 126 | 0 |
| `ema_trend_regime` | 8.6% | 8.7% | -11.1% | 0.057 | 0.187 | 167 | 0 |
| `sma_trend_fast_slow` | 6.1% | 8.5% | -16.4% | 0.122 | 0.217 | 215 | 0 |
| `sma_trend_slope` | 7.7% | 8.2% | -14.2% | 0.100 | 0.177 | 192 | 0 |
| `sma_trend_confirm` | 6.6% | 3.1% | -16.5% | 0.091 | 0.172 | 116 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.3% | 0.304 | 0.429 | 42 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.092 | 0.311 | 42 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 21 | 21 | 29.7% | 28.1% | 0.143 | 9.3 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 21 | 21 | 29.1% | 27.4% | 0.385 | 8.3 |
| `sma_trend_period175` | 21 | 21 | 27.3% | 25.7% | 0.111 | 8.3 |
| `sma_trend_period50` | 21 | 21 | 27.2% | 25.4% | 0.190 | 8.3 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 21 | 21 | 27.1% | 25.5% | 0.414 | 7.3 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 21 | 21 | 26.5% | 25.0% | 0.123 | 9.3 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 21 | 21 | 25.4% | 24.5% | 0.417 | 10.3 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 18 | 18 | 25.1% | 22.0% | 0.163 | 9.3 |
| `sma_trend_period225` | 21 | 21 | 24.9% | 23.1% | 0.139 | 9.3 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 21 | 21 | 24.5% | 22.7% | 0.399 | 8.3 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 21 | 7.0% | -5.7% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 18 | 6.8% | -1.8% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 16 | 4.9% | -2.2% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 21/21 runs (mean holdout 29.7%, worst 28.1%, mean DSR 0.143)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 21/21 runs (mean holdout 29.1%, worst 27.4%, mean DSR 0.385)
- KEEP: `sma_trend_period175` was positive in 21/21 runs (mean holdout 27.3%, worst 25.7%, mean DSR 0.111)
- KEEP: `sma_trend_period50` was positive in 21/21 runs (mean holdout 27.2%, worst 25.4%, mean DSR 0.190)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 21/21 runs (mean holdout 27.1%, worst 25.5%, mean DSR 0.414)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.1%) - add more parameters to it


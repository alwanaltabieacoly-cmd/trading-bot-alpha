# Deep research report

- Runs analysed: **22**
- Candidates per run: ~124
- Cumulative candidates evaluated: **2,800**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-24 12:47:10+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3515** (min 0.1793, max 0.612, over 22 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.9% | 20.5% | -16.4% | 0.149 | 0.202 | 242 | 0 |
| `sma_trend_vol_filter` | 14.5% | 14.1% | -10.4% | 0.122 | 0.569 | 733 | 0 |
| `sma_trend_efficiency` | 13.2% | 12.3% | -13.7% | 0.241 | 0.478 | 285 | 0 |
| `ema_trend` | 11.4% | 12.2% | -15.1% | 0.109 | 0.155 | 132 | 0 |
| `sma_trend_fast_slow` | 6.2% | 8.7% | -16.4% | 0.123 | 0.217 | 225 | 0 |
| `ema_trend_regime` | 8.6% | 8.7% | -11.1% | 0.057 | 0.187 | 176 | 0 |
| `sma_trend_slope` | 7.8% | 8.3% | -14.2% | 0.101 | 0.177 | 204 | 0 |
| `sma_trend_confirm` | 6.7% | 3.8% | -16.5% | 0.092 | 0.172 | 124 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.2% | 0.304 | 0.429 | 44 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.091 | 0.311 | 44 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 22 | 22 | 29.8% | 28.1% | 0.144 | 9.3 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 22 | 22 | 29.2% | 27.4% | 0.389 | 8.3 |
| `sma_trend_period175` | 22 | 22 | 27.3% | 25.7% | 0.112 | 8.3 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 22 | 22 | 27.2% | 25.5% | 0.417 | 7.3 |
| `sma_trend_period50` | 22 | 22 | 27.2% | 25.4% | 0.190 | 8.3 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 22 | 22 | 26.5% | 25.0% | 0.127 | 9.3 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 22 | 22 | 25.3% | 24.5% | 0.418 | 10.3 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 19 | 19 | 25.0% | 22.0% | 0.166 | 9.4 |
| `sma_trend_period225` | 22 | 22 | 24.9% | 23.1% | 0.141 | 9.3 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 22 | 22 | 24.6% | 22.7% | 0.403 | 8.3 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 22 | 7.0% | -5.6% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 19 | 6.8% | -1.7% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 17 | 4.9% | -2.1% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 12 | 13.6% | -1.6% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 22/22 runs (mean holdout 29.8%, worst 28.1%, mean DSR 0.144)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 22/22 runs (mean holdout 29.2%, worst 27.4%, mean DSR 0.389)
- KEEP: `sma_trend_period175` was positive in 22/22 runs (mean holdout 27.3%, worst 25.7%, mean DSR 0.112)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 22/22 runs (mean holdout 27.2%, worst 25.5%, mean DSR 0.417)
- KEEP: `sma_trend_period50` was positive in 22/22 runs (mean holdout 27.2%, worst 25.4%, mean DSR 0.190)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.2%) - add more parameters to it


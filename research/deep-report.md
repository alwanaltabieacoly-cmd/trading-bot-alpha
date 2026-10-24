# Deep research report

- Runs analysed: **24**
- Candidates per run: ~124
- Cumulative candidates evaluated: **3,084**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-24 22:34:55+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3671** (min 0.1793, max 0.612, over 24 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.9% | 20.5% | -16.4% | 0.151 | 0.202 | 264 | 0 |
| `sma_trend_vol_filter` | 14.4% | 14.0% | -10.4% | 0.125 | 0.569 | 801 | 0 |
| `sma_trend_efficiency` | 13.1% | 12.3% | -13.7% | 0.245 | 0.478 | 315 | 0 |
| `ema_trend` | 11.5% | 12.2% | -15.1% | 0.109 | 0.155 | 144 | 0 |
| `sma_trend_fast_slow` | 6.3% | 8.7% | -16.4% | 0.124 | 0.217 | 245 | 0 |
| `ema_trend_regime` | 8.7% | 8.7% | -11.1% | 0.059 | 0.187 | 194 | 0 |
| `sma_trend_slope` | 7.9% | 8.3% | -14.2% | 0.102 | 0.177 | 227 | 0 |
| `sma_trend_confirm` | 6.8% | 4.7% | -16.5% | 0.092 | 0.172 | 140 | 0 |
| `donchian_trend` | 2.4% | 1.7% | -4.2% | 0.303 | 0.429 | 48 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 0.9% | -3.0% | 0.089 | 0.311 | 48 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 24 | 24 | 29.7% | 28.1% | 0.146 | 9.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 24 | 24 | 29.2% | 27.4% | 0.396 | 8.4 |
| `sma_trend_period175` | 24 | 24 | 27.3% | 25.7% | 0.114 | 8.4 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 24 | 24 | 27.2% | 25.5% | 0.423 | 7.4 |
| `sma_trend_period50` | 24 | 24 | 27.0% | 25.4% | 0.191 | 8.4 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 24 | 24 | 26.5% | 25.0% | 0.133 | 9.4 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 24 | 24 | 25.3% | 24.5% | 0.421 | 10.3 |
| `sma_trend_period225` | 24 | 24 | 24.9% | 23.1% | 0.143 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 24 | 24 | 24.7% | 22.7% | 0.410 | 8.4 |
| `sma_trend_efficiency_period200_er_n30_er_min0.2` | 21 | 21 | 24.6% | 21.3% | 0.171 | 9.4 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 24 | 6.9% | -5.4% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 21 | 6.8% | -1.7% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 24/24 runs (mean holdout 29.7%, worst 28.1%, mean DSR 0.146)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 24/24 runs (mean holdout 29.2%, worst 27.4%, mean DSR 0.396)
- KEEP: `sma_trend_period175` was positive in 24/24 runs (mean holdout 27.3%, worst 25.7%, mean DSR 0.114)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 24/24 runs (mean holdout 27.2%, worst 25.5%, mean DSR 0.423)
- KEEP: `sma_trend_period50` was positive in 24/24 runs (mean holdout 27.0%, worst 25.4%, mean DSR 0.191)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.2%) - add more parameters to it


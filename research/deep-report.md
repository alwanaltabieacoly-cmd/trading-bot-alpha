# Deep research report

- Runs analysed: **40**
- Candidates per run: ~142
- Cumulative candidates evaluated: **5,356**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-29 01:05:22+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4331** (min 0.1793, max 0.612, over 40 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.9% | 22.7% | -16.4% | 0.157 | 0.203 | 440 | 0 |
| `sma_trend_vol_filter` | 16.0% | 15.3% | -10.4% | 0.134 | 0.569 | 1333 | 0 |
| `sma_trend_efficiency` | 13.1% | 14.0% | -13.8% | 0.259 | 0.478 | 555 | 0 |
| `ema_trend` | 13.3% | 13.1% | -15.3% | 0.111 | 0.155 | 240 | 0 |
| `sma_trend_slope` | 9.6% | 10.6% | -14.3% | 0.106 | 0.177 | 419 | 0 |
| `ema_trend_regime` | 10.5% | 10.0% | -11.1% | 0.064 | 0.187 | 338 | 0 |
| `sma_trend_fast_slow` | 8.0% | 9.1% | -16.3% | 0.130 | 0.217 | 429 | 0 |
| `sma_trend_confirm` | 8.7% | 6.8% | -16.5% | 0.096 | 0.172 | 268 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.301 | 0.429 | 80 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.082 | 0.311 | 80 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 40 | 40 | 31.5% | 28.1% | 0.156 | 9.6 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 40 | 40 | 31.4% | 27.4% | 0.427 | 8.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 40 | 40 | 29.3% | 25.5% | 0.448 | 8.1 |
| `sma_trend_period50` | 40 | 40 | 29.1% | 25.4% | 0.192 | 8.8 |
| `sma_trend_period175` | 40 | 40 | 29.0% | 25.7% | 0.121 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 40 | 40 | 28.7% | 25.0% | 0.163 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 40 | 40 | 27.0% | 22.7% | 0.440 | 8.6 |
| `sma_trend_period225` | 40 | 40 | 26.9% | 23.1% | 0.152 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 40 | 40 | 26.7% | 24.5% | 0.430 | 10.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 40 | 40 | 24.6% | 20.7% | 0.092 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 37 | 6.8% | -1.3% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 32 | 6.8% | -4.3% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_period200` was positive in 40/40 runs (mean holdout 31.5%, worst 28.1%, mean DSR 0.156)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 40/40 runs (mean holdout 31.4%, worst 27.4%, mean DSR 0.427)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 40/40 runs (mean holdout 29.3%, worst 25.5%, mean DSR 0.448)
- KEEP: `sma_trend_period50` was positive in 40/40 runs (mean holdout 29.1%, worst 25.4%, mean DSR 0.192)
- KEEP: `sma_trend_period175` was positive in 40/40 runs (mean holdout 29.0%, worst 25.7%, mean DSR 0.121)
- FAMILY `sma_trend` has the best median holdout CAGR (22.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.3%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (14.0%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.1%) - add more parameters to it


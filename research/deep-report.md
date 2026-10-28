# Deep research report

- Runs analysed: **38**
- Candidates per run: ~142
- Cumulative candidates evaluated: **5,072**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-28 16:11:29+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4286** (min 0.1793, max 0.612, over 38 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.7% | 22.2% | -16.4% | 0.157 | 0.203 | 418 | 0 |
| `sma_trend_vol_filter` | 15.8% | 15.1% | -10.4% | 0.133 | 0.569 | 1267 | 0 |
| `sma_trend_efficiency` | 13.1% | 13.9% | -13.8% | 0.258 | 0.478 | 525 | 0 |
| `ema_trend` | 13.2% | 13.0% | -15.3% | 0.111 | 0.155 | 228 | 0 |
| `sma_trend_slope` | 9.4% | 10.6% | -14.3% | 0.106 | 0.177 | 395 | 0 |
| `ema_trend_regime` | 10.4% | 9.9% | -11.1% | 0.064 | 0.187 | 320 | 0 |
| `sma_trend_fast_slow` | 7.9% | 9.1% | -16.3% | 0.130 | 0.217 | 406 | 0 |
| `sma_trend_confirm` | 8.5% | 6.4% | -16.5% | 0.096 | 0.172 | 252 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.301 | 0.429 | 76 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.082 | 0.311 | 76 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_period200` | 38 | 38 | 31.4% | 28.1% | 0.155 | 9.6 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 38 | 38 | 31.2% | 27.4% | 0.425 | 8.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 38 | 38 | 29.1% | 25.5% | 0.446 | 8.0 |
| `sma_trend_period50` | 38 | 38 | 28.9% | 25.4% | 0.193 | 8.8 |
| `sma_trend_period175` | 38 | 38 | 28.8% | 25.7% | 0.121 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 38 | 38 | 28.5% | 25.0% | 0.161 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 38 | 38 | 26.8% | 22.7% | 0.437 | 8.6 |
| `sma_trend_period225` | 38 | 38 | 26.7% | 23.1% | 0.152 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 38 | 38 | 26.6% | 24.5% | 0.429 | 10.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 38 | 38 | 24.4% | 20.7% | 0.090 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 35 | 6.8% | -1.3% |
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

- KEEP: `sma_trend_period200` was positive in 38/38 runs (mean holdout 31.4%, worst 28.1%, mean DSR 0.155)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 38/38 runs (mean holdout 31.2%, worst 27.4%, mean DSR 0.425)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 38/38 runs (mean holdout 29.1%, worst 25.5%, mean DSR 0.446)
- KEEP: `sma_trend_period50` was positive in 38/38 runs (mean holdout 28.9%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_period175` was positive in 38/38 runs (mean holdout 28.8%, worst 25.7%, mean DSR 0.121)
- FAMILY `sma_trend` has the best median holdout CAGR (22.2%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.9%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.0%) - add more parameters to it


# Deep research report

- Runs analysed: **50**
- Candidates per run: ~142
- Cumulative candidates evaluated: **6,776**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-31 12:48:19+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4411** (min 0.1793, max 0.612, over 50 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 22.0% | 22.2% | -16.5% | 0.159 | 0.203 | 550 | 0 |
| `sma_trend_vol_filter` | 16.3% | 15.6% | -10.4% | 0.137 | 0.579 | 1663 | 0 |
| `ema_trend` | 13.2% | 14.1% | -15.5% | 0.112 | 0.155 | 300 | 0 |
| `sma_trend_efficiency` | 12.9% | 13.4% | -13.9% | 0.263 | 0.478 | 708 | 0 |
| `ema_trend_regime` | 10.7% | 10.7% | -11.2% | 0.066 | 0.202 | 428 | 0 |
| `sma_trend_slope` | 9.6% | 10.6% | -14.5% | 0.108 | 0.179 | 539 | 0 |
| `sma_trend_fast_slow` | 8.4% | 9.8% | -16.3% | 0.133 | 0.221 | 539 | 0 |
| `sma_trend_confirm` | 8.7% | 6.8% | -16.7% | 0.098 | 0.174 | 343 | 0 |
| `donchian_trend` | 2.4% | 2.0% | -4.2% | 0.301 | 0.429 | 100 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.079 | 0.311 | 100 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 50 | 50 | 31.8% | 27.4% | 0.438 | 8.7 |
| `sma_trend_period200` | 50 | 50 | 31.6% | 28.1% | 0.159 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 50 | 50 | 29.7% | 25.5% | 0.457 | 8.5 |
| `sma_trend_period50` | 50 | 50 | 29.2% | 25.4% | 0.193 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 50 | 50 | 29.1% | 25.0% | 0.174 | 9.7 |
| `sma_trend_period175` | 50 | 50 | 29.1% | 25.7% | 0.123 | 9.0 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 50 | 50 | 27.4% | 22.7% | 0.450 | 8.7 |
| `sma_trend_period225` | 50 | 50 | 27.0% | 23.1% | 0.155 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 50 | 50 | 26.9% | 24.5% | 0.435 | 10.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 50 | 50 | 25.1% | 20.7% | 0.099 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 42 | 6.7% | -3.4% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 9 | 10.2% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 50/50 runs (mean holdout 31.8%, worst 27.4%, mean DSR 0.438)
- KEEP: `sma_trend_period200` was positive in 50/50 runs (mean holdout 31.6%, worst 28.1%, mean DSR 0.159)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 50/50 runs (mean holdout 29.7%, worst 25.5%, mean DSR 0.457)
- KEEP: `sma_trend_period50` was positive in 50/50 runs (mean holdout 29.2%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 50/50 runs (mean holdout 29.1%, worst 25.0%, mean DSR 0.174)
- FAMILY `sma_trend` has the best median holdout CAGR (22.2%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.6%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.4%) - add more parameters to it


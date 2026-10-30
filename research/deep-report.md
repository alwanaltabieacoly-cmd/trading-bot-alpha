# Deep research report

- Runs analysed: **45**
- Candidates per run: ~142
- Cumulative candidates evaluated: **6,066**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-30 07:18:28+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4403** (min 0.1793, max 0.612, over 45 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 22.1% | 22.7% | -16.4% | 0.158 | 0.203 | 495 | 0 |
| `sma_trend_vol_filter` | 16.2% | 15.4% | -10.4% | 0.135 | 0.578 | 1498 | 0 |
| `sma_trend_efficiency` | 13.0% | 13.9% | -13.8% | 0.261 | 0.478 | 631 | 0 |
| `ema_trend` | 13.4% | 13.6% | -15.3% | 0.111 | 0.155 | 270 | 0 |
| `sma_trend_slope` | 9.7% | 11.1% | -14.4% | 0.107 | 0.179 | 479 | 0 |
| `ema_trend_regime` | 10.7% | 10.5% | -11.2% | 0.065 | 0.200 | 383 | 0 |
| `sma_trend_fast_slow` | 8.2% | 9.4% | -16.3% | 0.131 | 0.221 | 484 | 0 |
| `sma_trend_confirm` | 8.8% | 6.9% | -16.6% | 0.097 | 0.174 | 308 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.301 | 0.429 | 90 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.080 | 0.311 | 90 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 45 | 45 | 31.7% | 27.4% | 0.433 | 8.7 |
| `sma_trend_period200` | 45 | 45 | 31.7% | 28.1% | 0.158 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 45 | 45 | 29.6% | 25.5% | 0.453 | 8.3 |
| `sma_trend_period50` | 45 | 45 | 29.2% | 25.4% | 0.192 | 8.8 |
| `sma_trend_period175` | 45 | 45 | 29.2% | 25.7% | 0.122 | 9.0 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 45 | 45 | 29.0% | 25.0% | 0.169 | 9.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 45 | 45 | 27.3% | 22.7% | 0.445 | 8.7 |
| `sma_trend_period225` | 45 | 45 | 27.1% | 23.1% | 0.154 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 45 | 45 | 26.8% | 24.5% | 0.432 | 10.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 45 | 45 | 24.9% | 20.7% | 0.095 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 41 | 6.8% | -1.2% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 37 | 6.8% | -3.8% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 4 | 10.9% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 45/45 runs (mean holdout 31.7%, worst 27.4%, mean DSR 0.433)
- KEEP: `sma_trend_period200` was positive in 45/45 runs (mean holdout 31.7%, worst 28.1%, mean DSR 0.158)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 45/45 runs (mean holdout 29.6%, worst 25.5%, mean DSR 0.453)
- KEEP: `sma_trend_period50` was positive in 45/45 runs (mean holdout 29.2%, worst 25.4%, mean DSR 0.192)
- KEEP: `sma_trend_period175` was positive in 45/45 runs (mean holdout 29.2%, worst 25.7%, mean DSR 0.122)
- FAMILY `sma_trend` has the best median holdout CAGR (22.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.4%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.9%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.6%) - add more parameters to it


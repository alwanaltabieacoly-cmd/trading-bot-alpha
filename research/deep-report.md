# Deep research report

- Runs analysed: **58**
- Candidates per run: ~142
- Cumulative candidates evaluated: **7,912**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-02 06:25:46+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4433** (min 0.1793, max 0.612, over 58 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.9% | 21.9% | -16.6% | 0.161 | 0.203 | 638 | 0 |
| `sma_trend_vol_filter` | 16.5% | 15.7% | -10.4% | 0.140 | 0.579 | 1926 | 0 |
| `ema_trend` | 13.0% | 14.0% | -15.6% | 0.112 | 0.155 | 348 | 0 |
| `sma_trend_efficiency` | 12.9% | 13.1% | -13.9% | 0.265 | 0.478 | 836 | 0 |
| `ema_trend_regime` | 10.7% | 10.7% | -11.2% | 0.068 | 0.203 | 500 | 0 |
| `sma_trend_slope` | 9.4% | 10.4% | -14.7% | 0.109 | 0.179 | 633 | 0 |
| `sma_trend_fast_slow` | 8.6% | 9.9% | -16.3% | 0.134 | 0.221 | 632 | 0 |
| `sma_trend_confirm` | 8.6% | 6.8% | -16.8% | 0.098 | 0.174 | 398 | 0 |
| `donchian_trend` | 2.5% | 2.0% | -4.1% | 0.300 | 0.429 | 116 | 0 |
| `donchian_trend_vol_filter` | 1.5% | 1.1% | -3.0% | 0.078 | 0.311 | 122 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 58 | 58 | 31.9% | 27.4% | 0.445 | 8.7 |
| `sma_trend_period200` | 58 | 58 | 31.4% | 28.1% | 0.161 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 58 | 58 | 29.9% | 25.5% | 0.463 | 8.7 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 58 | 58 | 29.3% | 25.0% | 0.180 | 9.7 |
| `sma_trend_period50` | 58 | 58 | 29.2% | 25.4% | 0.194 | 8.9 |
| `sma_trend_period175` | 58 | 58 | 29.0% | 25.7% | 0.125 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 58 | 58 | 27.6% | 22.7% | 0.457 | 8.7 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 58 | 58 | 26.9% | 24.5% | 0.439 | 10.5 |
| `sma_trend_period225` | 58 | 58 | 26.9% | 23.1% | 0.157 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 58 | 58 | 25.3% | 20.7% | 0.104 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 45 | 6.7% | -3.2% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_confirm_slow_period100_fast_period50` | 17 | 10.0% | -0.4% |
| `sma_trend_slope_period100_slope_bars10` | 15 | 13.4% | -1.3% |
| `sma_trend_confirm_slow_period100_fast_period20` | 13 | 10.1% | -0.7% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 58/58 runs (mean holdout 31.9%, worst 27.4%, mean DSR 0.445)
- KEEP: `sma_trend_period200` was positive in 58/58 runs (mean holdout 31.4%, worst 28.1%, mean DSR 0.161)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 58/58 runs (mean holdout 29.9%, worst 25.5%, mean DSR 0.463)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 58/58 runs (mean holdout 29.3%, worst 25.0%, mean DSR 0.180)
- KEEP: `sma_trend_period50` was positive in 58/58 runs (mean holdout 29.2%, worst 25.4%, mean DSR 0.194)
- FAMILY `sma_trend` has the best median holdout CAGR (21.9%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (14.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.1%) - add more parameters to it


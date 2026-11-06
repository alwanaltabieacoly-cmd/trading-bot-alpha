# Deep research report

- Runs analysed: **73**
- Candidates per run: ~142
- Cumulative candidates evaluated: **10,042**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-06 19:34:57+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4415** (min 0.1793, max 0.612, over 73 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.2% | 21.1% | -16.8% | 0.163 | 0.211 | 803 | 0 |
| `sma_trend_vol_filter` | 16.3% | 15.5% | -10.4% | 0.144 | 0.598 | 2422 | 0 |
| `ema_trend` | 12.4% | 13.1% | -15.8% | 0.113 | 0.155 | 436 | 0 |
| `sma_trend_efficiency` | 12.7% | 13.0% | -14.0% | 0.269 | 0.487 | 1076 | 0 |
| `ema_trend_regime` | 10.4% | 10.5% | -11.3% | 0.070 | 0.228 | 635 | 0 |
| `sma_trend_slope` | 8.9% | 9.7% | -14.9% | 0.110 | 0.182 | 803 | 0 |
| `sma_trend_fast_slow` | 8.3% | 9.4% | -16.3% | 0.136 | 0.226 | 795 | 0 |
| `sma_trend_confirm` | 8.1% | 6.4% | -17.0% | 0.100 | 0.178 | 495 | 0 |
| `donchian_trend` | 2.7% | 2.0% | -4.1% | 0.300 | 0.429 | 159 | 0 |
| `donchian_trend_vol_filter` | 1.6% | 1.2% | -2.9% | 0.076 | 0.311 | 157 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 73 | 73 | 31.6% | 27.4% | 0.455 | 8.8 |
| `sma_trend_period200` | 73 | 73 | 30.7% | 24.4% | 0.164 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 73 | 73 | 29.7% | 24.6% | 0.471 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 73 | 73 | 29.0% | 25.0% | 0.191 | 9.8 |
| `sma_trend_period175` | 73 | 73 | 28.4% | 20.6% | 0.127 | 9.4 |
| `sma_trend_period50` | 73 | 73 | 28.1% | 18.8% | 0.196 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 73 | 73 | 27.1% | 22.6% | 0.466 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 73 | 73 | 26.6% | 21.7% | 0.448 | 10.3 |
| `sma_trend_period225` | 73 | 73 | 26.0% | 19.1% | 0.160 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 73 | 73 | 24.9% | 20.7% | 0.111 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 60 | 6.6% | -3.0% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 32 | 9.9% | -0.7% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 21 | 5.0% | -2.0% |
| `sma_trend_confirm_slow_period100_fast_period20` | 20 | 9.9% | -0.7% |
| `sma_trend_slope_period100_slope_bars10` | 19 | 13.1% | -1.1% |
| `sma_trend_slope_period150_slope_bars40` | 18 | 12.8% | -2.9% |
| `sma_trend_confirm_slow_period150_fast_period50` | 13 | 12.6% | -0.6% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 73/73 runs (mean holdout 31.6%, worst 27.4%, mean DSR 0.455)
- KEEP: `sma_trend_period200` was positive in 73/73 runs (mean holdout 30.7%, worst 24.4%, mean DSR 0.164)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 73/73 runs (mean holdout 29.7%, worst 24.6%, mean DSR 0.471)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 73/73 runs (mean holdout 29.0%, worst 25.0%, mean DSR 0.191)
- KEEP: `sma_trend_period175` was positive in 73/73 runs (mean holdout 28.4%, worst 20.6%, mean DSR 0.127)
- FAMILY `sma_trend` has the best median holdout CAGR (21.1%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.5%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.0%) - add more parameters to it


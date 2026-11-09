# Deep research report

- Runs analysed: **82**
- Candidates per run: ~142
- Cumulative candidates evaluated: **11,320**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-09 01:01:58+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4224** (min 0.1793, max 0.612, over 82 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.2% | 20.5% | -16.9% | 0.164 | 0.226 | 902 | 0 |
| `sma_trend_vol_filter` | 15.7% | 15.0% | -10.4% | 0.146 | 0.607 | 2711 | 0 |
| `sma_trend_efficiency` | 12.4% | 12.7% | -14.1% | 0.271 | 0.488 | 1220 | 0 |
| `ema_trend` | 11.6% | 12.4% | -15.9% | 0.113 | 0.155 | 481 | 0 |
| `ema_trend_regime` | 9.9% | 9.8% | -11.3% | 0.072 | 0.241 | 715 | 0 |
| `sma_trend_fast_slow` | 7.6% | 8.6% | -16.4% | 0.138 | 0.226 | 868 | 0 |
| `sma_trend_slope` | 8.2% | 8.5% | -15.0% | 0.111 | 0.183 | 877 | 0 |
| `sma_trend_confirm` | 7.4% | 5.8% | -17.0% | 0.100 | 0.178 | 533 | 0 |
| `donchian_trend` | 2.8% | 2.0% | -4.0% | 0.300 | 0.429 | 186 | 0 |
| `donchian_trend_vol_filter` | 1.7% | 1.2% | -2.9% | 0.075 | 0.311 | 178 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 82 | 82 | 30.9% | 24.7% | 0.459 | 8.8 |
| `sma_trend_period200` | 82 | 82 | 29.7% | 21.4% | 0.165 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 82 | 82 | 28.8% | 21.2% | 0.476 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 82 | 82 | 28.4% | 22.9% | 0.196 | 9.8 |
| `sma_trend_period175` | 82 | 82 | 27.2% | 17.4% | 0.128 | 9.3 |
| `sma_trend_period50` | 82 | 82 | 26.5% | 13.2% | 0.199 | 8.8 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 82 | 82 | 26.3% | 19.6% | 0.471 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 82 | 82 | 25.6% | 17.2% | 0.455 | 10.0 |
| `sma_trend_period225` | 82 | 82 | 25.0% | 16.2% | 0.161 | 9.5 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 82 | 82 | 24.2% | 18.1% | 0.115 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 69 | 6.6% | -3.5% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 41 | 9.9% | -1.8% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 30 | 5.1% | -2.9% |
| `sma_trend_confirm_slow_period100_fast_period20` | 29 | 9.9% | -1.5% |
| `sma_trend_slope_period100_slope_bars10` | 28 | 12.8% | -1.5% |
| `sma_trend_slope_period150_slope_bars40` | 27 | 12.6% | -3.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 21 | 12.0% | -1.0% |
| `ema_trend_fast50_slow300` | 11 | 8.2% | -2.7% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 9 | 11.5% | -1.6% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 82/82 runs (mean holdout 30.9%, worst 24.7%, mean DSR 0.459)
- KEEP: `sma_trend_period200` was positive in 82/82 runs (mean holdout 29.7%, worst 21.4%, mean DSR 0.165)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 82/82 runs (mean holdout 28.8%, worst 21.2%, mean DSR 0.476)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 82/82 runs (mean holdout 28.4%, worst 22.9%, mean DSR 0.196)
- KEEP: `sma_trend_period175` was positive in 82/82 runs (mean holdout 27.2%, worst 17.4%, mean DSR 0.128)
- FAMILY `sma_trend` has the best median holdout CAGR (20.5%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.4%) - add more parameters to it


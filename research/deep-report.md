# Deep research report

- Runs analysed: **84**
- Candidates per run: ~142
- Cumulative candidates evaluated: **11,604**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-09 18:57:25+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4186** (min 0.1793, max 0.612, over 84 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.0% | 20.4% | -16.9% | 0.164 | 0.226 | 924 | 0 |
| `sma_trend_vol_filter` | 15.6% | 15.0% | -10.4% | 0.146 | 0.607 | 2781 | 0 |
| `sma_trend_efficiency` | 12.4% | 12.7% | -14.1% | 0.271 | 0.488 | 1252 | 0 |
| `ema_trend` | 11.5% | 12.3% | -16.0% | 0.113 | 0.155 | 491 | 0 |
| `ema_trend_regime` | 9.8% | 9.8% | -11.3% | 0.072 | 0.241 | 735 | 0 |
| `sma_trend_fast_slow` | 7.5% | 8.5% | -16.4% | 0.138 | 0.226 | 886 | 0 |
| `sma_trend_slope` | 8.1% | 8.4% | -15.0% | 0.111 | 0.183 | 897 | 0 |
| `sma_trend_confirm` | 7.3% | 5.6% | -17.1% | 0.100 | 0.178 | 541 | 0 |
| `donchian_trend` | 2.9% | 2.1% | -4.0% | 0.300 | 0.429 | 192 | 0 |
| `donchian_trend_vol_filter` | 1.8% | 1.2% | -2.9% | 0.075 | 0.311 | 182 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 84 | 84 | 30.8% | 24.7% | 0.460 | 8.8 |
| `sma_trend_period200` | 84 | 84 | 29.5% | 21.4% | 0.165 | 9.5 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 84 | 84 | 28.7% | 21.2% | 0.477 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 84 | 84 | 28.3% | 22.9% | 0.197 | 9.8 |
| `sma_trend_period175` | 84 | 84 | 27.0% | 17.4% | 0.128 | 9.3 |
| `sma_trend_period50` | 84 | 84 | 26.3% | 13.2% | 0.199 | 8.8 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 84 | 84 | 26.2% | 19.6% | 0.472 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 84 | 84 | 25.4% | 17.2% | 0.457 | 10.0 |
| `sma_trend_period225` | 84 | 84 | 24.8% | 16.2% | 0.161 | 9.5 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 84 | 84 | 24.1% | 18.1% | 0.115 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 71 | 6.6% | -3.6% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 43 | 9.9% | -1.9% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 32 | 5.1% | -2.9% |
| `sma_trend_confirm_slow_period100_fast_period20` | 31 | 9.9% | -1.4% |
| `sma_trend_slope_period100_slope_bars10` | 30 | 12.8% | -1.5% |
| `sma_trend_slope_period150_slope_bars40` | 29 | 12.5% | -3.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 23 | 12.0% | -0.9% |
| `ema_trend_fast50_slow300` | 13 | 8.2% | -2.6% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 11 | 11.5% | -1.3% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 84/84 runs (mean holdout 30.8%, worst 24.7%, mean DSR 0.460)
- KEEP: `sma_trend_period200` was positive in 84/84 runs (mean holdout 29.5%, worst 21.4%, mean DSR 0.165)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 84/84 runs (mean holdout 28.7%, worst 21.2%, mean DSR 0.477)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 84/84 runs (mean holdout 28.3%, worst 22.9%, mean DSR 0.197)
- KEEP: `sma_trend_period175` was positive in 84/84 runs (mean holdout 27.0%, worst 17.4%, mean DSR 0.128)
- FAMILY `sma_trend` has the best median holdout CAGR (20.4%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.7%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (12.3%) - add more parameters to it


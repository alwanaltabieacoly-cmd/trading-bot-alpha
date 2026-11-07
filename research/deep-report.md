# Deep research report

- Runs analysed: **75**
- Candidates per run: ~142
- Cumulative candidates evaluated: **10,326**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-07 06:13:33+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4368** (min 0.1793, max 0.612, over 75 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 21.0% | 21.0% | -16.8% | 0.163 | 0.213 | 825 | 0 |
| `sma_trend_vol_filter` | 16.1% | 15.4% | -10.4% | 0.144 | 0.600 | 2484 | 0 |
| `ema_trend` | 12.2% | 13.0% | -15.8% | 0.113 | 0.155 | 446 | 0 |
| `sma_trend_efficiency` | 12.6% | 12.8% | -14.0% | 0.269 | 0.488 | 1108 | 0 |
| `ema_trend_regime` | 10.3% | 10.3% | -11.3% | 0.071 | 0.231 | 651 | 0 |
| `sma_trend_slope` | 8.8% | 9.6% | -14.9% | 0.110 | 0.183 | 819 | 0 |
| `sma_trend_fast_slow` | 8.1% | 9.1% | -16.3% | 0.137 | 0.226 | 811 | 0 |
| `sma_trend_confirm` | 7.9% | 6.1% | -17.0% | 0.100 | 0.178 | 503 | 0 |
| `donchian_trend` | 2.7% | 2.0% | -4.1% | 0.300 | 0.429 | 165 | 0 |
| `donchian_trend_vol_filter` | 1.6% | 1.2% | -2.9% | 0.076 | 0.311 | 161 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 75 | 75 | 31.4% | 24.8% | 0.456 | 8.8 |
| `sma_trend_period200` | 75 | 75 | 30.5% | 21.6% | 0.164 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 75 | 75 | 29.5% | 21.3% | 0.472 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 75 | 75 | 28.9% | 23.0% | 0.192 | 9.8 |
| `sma_trend_period175` | 75 | 75 | 28.1% | 17.6% | 0.127 | 9.4 |
| `sma_trend_period50` | 75 | 75 | 27.7% | 13.2% | 0.196 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 75 | 75 | 26.9% | 19.6% | 0.467 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 75 | 75 | 26.3% | 17.3% | 0.449 | 10.2 |
| `sma_trend_period225` | 75 | 75 | 25.8% | 16.4% | 0.160 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 75 | 75 | 24.7% | 18.1% | 0.112 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 62 | 6.6% | -3.2% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 34 | 9.9% | -1.0% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 23 | 5.0% | -2.3% |
| `sma_trend_confirm_slow_period100_fast_period20` | 22 | 9.9% | -1.0% |
| `sma_trend_slope_period100_slope_bars10` | 21 | 13.0% | -1.3% |
| `sma_trend_slope_period150_slope_bars40` | 20 | 12.7% | -3.1% |
| `sma_trend_confirm_slow_period150_fast_period50` | 15 | 12.4% | -0.8% |
| `ema_trend_fast50_slow300` | 4 | 8.1% | -2.1% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 75/75 runs (mean holdout 31.4%, worst 24.8%, mean DSR 0.456)
- KEEP: `sma_trend_period200` was positive in 75/75 runs (mean holdout 30.5%, worst 21.6%, mean DSR 0.164)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 75/75 runs (mean holdout 29.5%, worst 21.3%, mean DSR 0.472)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 75/75 runs (mean holdout 28.9%, worst 23.0%, mean DSR 0.192)
- KEEP: `sma_trend_period175` was positive in 75/75 runs (mean holdout 28.1%, worst 17.6%, mean DSR 0.127)
- FAMILY `sma_trend` has the best median holdout CAGR (21.0%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.4%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.8%) - add more parameters to it


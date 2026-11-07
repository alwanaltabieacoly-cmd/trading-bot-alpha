# Deep research report

- Runs analysed: **76**
- Candidates per run: ~142
- Cumulative candidates evaluated: **10,468**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-07 13:18:26+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4345** (min 0.1793, max 0.612, over 76 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 20.8% | 20.8% | -16.8% | 0.163 | 0.213 | 836 | 0 |
| `sma_trend_vol_filter` | 16.0% | 15.3% | -10.4% | 0.144 | 0.600 | 2515 | 0 |
| `ema_trend` | 12.1% | 13.0% | -15.9% | 0.113 | 0.155 | 451 | 0 |
| `sma_trend_efficiency` | 12.6% | 12.8% | -14.0% | 0.270 | 0.488 | 1124 | 0 |
| `ema_trend_regime` | 10.2% | 10.1% | -11.3% | 0.071 | 0.231 | 659 | 0 |
| `sma_trend_slope` | 8.7% | 9.4% | -14.9% | 0.110 | 0.183 | 827 | 0 |
| `sma_trend_fast_slow` | 8.0% | 9.0% | -16.3% | 0.137 | 0.226 | 819 | 0 |
| `sma_trend_confirm` | 7.8% | 6.0% | -17.0% | 0.100 | 0.178 | 507 | 0 |
| `donchian_trend` | 2.7% | 2.0% | -4.1% | 0.300 | 0.429 | 168 | 0 |
| `donchian_trend_vol_filter` | 1.7% | 1.2% | -2.9% | 0.076 | 0.311 | 163 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 76 | 76 | 31.3% | 24.8% | 0.456 | 8.8 |
| `sma_trend_period200` | 76 | 76 | 30.3% | 21.5% | 0.164 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 76 | 76 | 29.4% | 21.3% | 0.473 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 76 | 76 | 28.8% | 23.0% | 0.193 | 9.8 |
| `sma_trend_period175` | 76 | 76 | 28.0% | 17.5% | 0.127 | 9.4 |
| `sma_trend_period50` | 76 | 76 | 27.5% | 13.2% | 0.197 | 8.9 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 76 | 76 | 26.8% | 19.6% | 0.468 | 8.8 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 76 | 76 | 26.2% | 17.3% | 0.449 | 10.2 |
| `sma_trend_period225` | 76 | 76 | 25.7% | 16.3% | 0.160 | 9.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 76 | 76 | 24.6% | 18.1% | 0.112 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 63 | 6.6% | -3.2% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period50` | 35 | 9.9% | -1.2% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 24 | 5.0% | -2.4% |
| `sma_trend_confirm_slow_period100_fast_period20` | 23 | 9.9% | -1.1% |
| `sma_trend_slope_period100_slope_bars10` | 22 | 13.0% | -1.3% |
| `sma_trend_slope_period150_slope_bars40` | 21 | 12.7% | -3.1% |
| `sma_trend_confirm_slow_period150_fast_period50` | 16 | 12.3% | -0.8% |
| `ema_trend_fast50_slow300` | 5 | 8.1% | -2.3% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 76/76 runs (mean holdout 31.3%, worst 24.8%, mean DSR 0.456)
- KEEP: `sma_trend_period200` was positive in 76/76 runs (mean holdout 30.3%, worst 21.5%, mean DSR 0.164)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 76/76 runs (mean holdout 29.4%, worst 21.3%, mean DSR 0.473)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 76/76 runs (mean holdout 28.8%, worst 23.0%, mean DSR 0.193)
- KEEP: `sma_trend_period175` was positive in 76/76 runs (mean holdout 28.0%, worst 17.5%, mean DSR 0.127)
- FAMILY `sma_trend` has the best median holdout CAGR (20.8%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.3%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (13.0%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.8%) - add more parameters to it


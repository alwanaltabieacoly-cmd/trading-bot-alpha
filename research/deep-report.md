# Deep research report

- Runs analysed: **97**
- Candidates per run: ~142
- Cumulative candidates evaluated: **13,450**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-13 17:53:53+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4022** (min 0.1793, max 0.612, over 97 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.3% | 19.7% | -17.0% | 0.166 | 0.226 | 1067 | 0 |
| `sma_trend_vol_filter` | 15.4% | 14.9% | -10.3% | 0.149 | 0.607 | 3214 | 0 |
| `sma_trend_efficiency` | 12.3% | 12.8% | -14.1% | 0.274 | 0.493 | 1460 | 0 |
| `ema_trend` | 10.8% | 11.5% | -16.1% | 0.114 | 0.155 | 559 | 0 |
| `ema_trend_regime` | 9.6% | 9.5% | -11.3% | 0.074 | 0.243 | 852 | 0 |
| `sma_trend_fast_slow` | 7.2% | 8.1% | -16.4% | 0.139 | 0.229 | 1013 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.1% | 0.111 | 0.184 | 1037 | 0 |
| `sma_trend_confirm` | 6.9% | 5.1% | -17.1% | 0.101 | 0.179 | 626 | 0 |
| `donchian_trend` | 3.2% | 2.3% | -4.0% | 0.299 | 0.429 | 231 | 0 |
| `donchian_trend_vol_filter` | 2.1% | 1.4% | -2.8% | 0.074 | 0.311 | 208 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 97 | 97 | 30.4% | 24.7% | 0.466 | 8.8 |
| `sma_trend_period200` | 97 | 97 | 28.6% | 20.5% | 0.167 | 9.4 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 97 | 97 | 28.2% | 21.2% | 0.481 | 8.8 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 97 | 97 | 28.0% | 22.9% | 0.204 | 9.8 |
| `sma_trend_period175` | 97 | 97 | 26.0% | 16.9% | 0.129 | 9.2 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 97 | 97 | 25.9% | 19.6% | 0.478 | 8.8 |
| `sma_trend_period50` | 97 | 97 | 25.7% | 13.2% | 0.202 | 8.7 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 97 | 97 | 24.9% | 17.2% | 0.467 | 9.8 |
| `sma_trend_period225` | 97 | 97 | 24.0% | 16.2% | 0.163 | 9.3 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 97 | 97 | 23.9% | 18.1% | 0.120 | 8.8 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 84 | 6.6% | -3.7% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 45 | 5.1% | -2.7% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_slope_period150_slope_bars40` | 42 | 12.4% | -3.6% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 97/97 runs (mean holdout 30.4%, worst 24.7%, mean DSR 0.466)
- KEEP: `sma_trend_period200` was positive in 97/97 runs (mean holdout 28.6%, worst 20.5%, mean DSR 0.167)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 97/97 runs (mean holdout 28.2%, worst 21.2%, mean DSR 0.481)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 97/97 runs (mean holdout 28.0%, worst 22.9%, mean DSR 0.204)
- KEEP: `sma_trend_period175` was positive in 97/97 runs (mean holdout 26.0%, worst 16.9%, mean DSR 0.129)
- FAMILY `sma_trend` has the best median holdout CAGR (19.7%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (14.9%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (12.8%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (11.5%) - add more parameters to it


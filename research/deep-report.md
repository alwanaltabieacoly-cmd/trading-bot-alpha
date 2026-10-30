# Deep research report

- Runs analysed: **47**
- Candidates per run: ~142
- Cumulative candidates evaluated: **6,350**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-10-30 19:59:58+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.4406** (min 0.1793, max 0.612, over 47 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 22.0% | 22.6% | -16.5% | 0.159 | 0.203 | 517 | 0 |
| `sma_trend_vol_filter` | 16.2% | 15.5% | -10.4% | 0.136 | 0.578 | 1564 | 0 |
| `ema_trend` | 13.3% | 14.1% | -15.4% | 0.111 | 0.155 | 282 | 0 |
| `sma_trend_efficiency` | 13.0% | 13.8% | -13.8% | 0.262 | 0.478 | 661 | 0 |
| `sma_trend_slope` | 9.6% | 10.7% | -14.4% | 0.107 | 0.179 | 503 | 0 |
| `ema_trend_regime` | 10.7% | 10.6% | -11.2% | 0.066 | 0.200 | 401 | 0 |
| `sma_trend_fast_slow` | 8.3% | 9.5% | -16.3% | 0.132 | 0.221 | 506 | 0 |
| `sma_trend_confirm` | 8.8% | 6.9% | -16.6% | 0.097 | 0.174 | 322 | 0 |
| `donchian_trend` | 2.4% | 1.9% | -4.2% | 0.301 | 0.429 | 94 | 0 |
| `donchian_trend_vol_filter` | 1.4% | 1.1% | -3.0% | 0.080 | 0.311 | 94 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 47 | 47 | 31.7% | 27.4% | 0.435 | 8.7 |
| `sma_trend_period200` | 47 | 47 | 31.6% | 28.1% | 0.158 | 9.6 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 47 | 47 | 29.6% | 25.5% | 0.455 | 8.4 |
| `sma_trend_period50` | 47 | 47 | 29.2% | 25.4% | 0.193 | 8.9 |
| `sma_trend_period175` | 47 | 47 | 29.1% | 25.7% | 0.123 | 9.0 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 47 | 47 | 29.0% | 25.0% | 0.171 | 9.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 47 | 47 | 27.3% | 22.7% | 0.447 | 8.7 |
| `sma_trend_period225` | 47 | 47 | 27.0% | 23.1% | 0.155 | 9.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 47 | 47 | 26.8% | 24.5% | 0.433 | 10.6 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 47 | 47 | 25.0% | 20.7% | 0.097 | 9.0 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 43 | 6.8% | -1.1% |
| `sma_trend_fast_slow_slow_period250_fast_period10` | 39 | 6.7% | -3.6% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 19 | 5.0% | -1.9% |
| `sma_trend_slope_period100_slope_bars10` | 13 | 13.5% | -1.5% |
| `sma_trend_confirm_slow_period150_fast_period50` | 12 | 12.7% | -0.7% |
| `sma_trend_confirm_slow_period100_fast_period20` | 12 | 10.1% | -0.7% |
| `sma_trend_slope_period150_slope_bars40` | 12 | 13.2% | -3.4% |
| `sma_trend_confirm_slow_period100_fast_period50` | 6 | 10.5% | -0.2% |
| `aapl_scalp_trend_sma_period200_ema_period21_rsi_period14_rsi_max55` | 3 | -8.3% | -14.8% |
| `sma_trend_rsi_filter_period150_rsi_period14_rsi_max80` | 3 | 10.5% | -2.5% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 47/47 runs (mean holdout 31.7%, worst 27.4%, mean DSR 0.435)
- KEEP: `sma_trend_period200` was positive in 47/47 runs (mean holdout 31.6%, worst 28.1%, mean DSR 0.158)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 47/47 runs (mean holdout 29.6%, worst 25.5%, mean DSR 0.455)
- KEEP: `sma_trend_period50` was positive in 47/47 runs (mean holdout 29.2%, worst 25.4%, mean DSR 0.193)
- KEEP: `sma_trend_period175` was positive in 47/47 runs (mean holdout 29.1%, worst 25.7%, mean DSR 0.123)
- FAMILY `sma_trend` has the best median holdout CAGR (22.6%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.5%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (14.1%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.8%) - add more parameters to it


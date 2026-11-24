# Deep research report

- Runs analysed: **132**
- Candidates per run: ~142
- Cumulative candidates evaluated: **18,420**
- Window: 2026-10-20 00:41:09+00:00 -> 2026-11-24 13:58:37+00:00

## Is the search actually working?

- Train-vs-holdout rank correlation: **0.3802** (min 0.1793, max 0.612, over 132 runs)
- Verdict: **search is informative**

> A correlation near 0 means the backtest ranking carries no information about future performance - the search is noise. Above 0.3 means the search genuinely finds something.

## Strategy families

| family | mean holdout CAGR | median | mean DD | mean DSR | max DSR | times basic | times gate |
|---|---|---|---|---|---|---|---|
| `sma_trend` | 19.2% | 19.6% | -17.1% | 0.168 | 0.226 | 1452 | 0 |
| `sma_trend_vol_filter` | 16.1% | 15.9% | -10.0% | 0.154 | 0.607 | 4316 | 0 |
| `sma_trend_efficiency` | 12.5% | 13.4% | -14.2% | 0.278 | 0.500 | 2020 | 0 |
| `ema_trend` | 10.2% | 10.6% | -16.6% | 0.115 | 0.155 | 769 | 0 |
| `ema_trend_regime` | 10.1% | 9.8% | -11.1% | 0.078 | 0.243 | 1137 | 0 |
| `sma_trend_fast_slow` | 7.3% | 8.1% | -16.4% | 0.141 | 0.233 | 1363 | 0 |
| `sma_trend_slope` | 7.6% | 7.5% | -15.2% | 0.113 | 0.186 | 1422 | 0 |
| `sma_trend_confirm` | 7.1% | 5.6% | -17.0% | 0.102 | 0.181 | 906 | 0 |
| `donchian_trend` | 3.8% | 2.8% | -3.9% | 0.299 | 0.429 | 336 | 0 |
| `donchian_trend_vol_filter` | 2.6% | 2.5% | -2.7% | 0.071 | 0.311 | 278 | 0 |
| `aapl_scalp_reversion` | 0.1% | 0.0% | -0.0% | 0.000 | 0.002 | 0 | 0 |
| `aapl_scalp_trend` | -5.0% | -2.7% | -4.0% | 0.037 | 0.215 | 3 | 0 |
| `sma_trend_rsi_filter` | -5.2% | -5.7% | -16.8% | 0.036 | 0.097 | 3 | 0 |

## Consistent winners (positive in every run seen)

| strategy | runs | positive | mean holdout | worst holdout | mean DSR | assets+ |
|---|---|---|---|---|---|---|
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` | 132 | 132 | 30.7% | 24.7% | 0.478 | 8.9 |
| `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` | 132 | 132 | 28.7% | 22.9% | 0.218 | 9.9 |
| `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` | 132 | 132 | 28.1% | 21.2% | 0.491 | 9.1 |
| `sma_trend_period200` | 132 | 132 | 28.0% | 20.5% | 0.170 | 9.3 |
| `sma_trend_period50` | 132 | 132 | 26.2% | 13.2% | 0.201 | 8.7 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct4.0` | 132 | 132 | 26.1% | 19.6% | 0.489 | 8.6 |
| `sma_trend_vol_filter_period100_vol_lookback30_vol_max_pct3.0` | 132 | 132 | 25.1% | 17.2% | 0.475 | 9.6 |
| `sma_trend_period175` | 132 | 132 | 25.0% | 16.9% | 0.132 | 9.4 |
| `sma_trend_vol_filter_period225_vol_lookback30_vol_max_pct3.0` | 132 | 132 | 24.4% | 18.1% | 0.130 | 8.6 |
| `sma_trend_period225` | 132 | 132 | 23.3% | 16.2% | 0.166 | 8.7 |

## Repeat overfits

| strategy | times | mean train | mean holdout |
|---|---|---|---|
| `sma_trend_fast_slow_slow_period250_fast_period10` | 119 | 6.5% | -3.3% |
| `sma_trend_fast_slow_slow_period150_fast_period10` | 80 | 4.9% | -1.8% |
| `sma_trend_slope_period150_slope_bars40` | 77 | 12.0% | -2.7% |
| `sma_trend_confirm_slow_period100_fast_period50` | 53 | 9.9% | -1.9% |
| `sma_trend_efficiency_period250_er_n20_er_min0.3` | 44 | 6.8% | -1.1% |
| `sma_trend_confirm_slow_period100_fast_period20` | 34 | 9.8% | -1.3% |
| `sma_trend_slope_period100_slope_bars10` | 33 | 12.7% | -1.4% |
| `sma_trend_confirm_slow_period150_fast_period50` | 26 | 11.8% | -1.0% |
| `ema_trend_fast50_slow300` | 23 | 8.2% | -2.4% |
| `sma_trend_fast_slow_slow_period250_fast_period50` | 14 | 11.5% | -1.2% |

## What to try next

- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct4.0` was positive in 132/132 runs (mean holdout 30.7%, worst 24.7%, mean DSR 0.478)
- KEEP: `sma_trend_vol_filter_period200_vol_lookback30_vol_max_pct3.0` was positive in 132/132 runs (mean holdout 28.7%, worst 22.9%, mean DSR 0.218)
- KEEP: `sma_trend_vol_filter_period175_vol_lookback30_vol_max_pct4.0` was positive in 132/132 runs (mean holdout 28.1%, worst 21.2%, mean DSR 0.491)
- KEEP: `sma_trend_period200` was positive in 132/132 runs (mean holdout 28.0%, worst 20.5%, mean DSR 0.170)
- KEEP: `sma_trend_period50` was positive in 132/132 runs (mean holdout 26.2%, worst 13.2%, mean DSR 0.201)
- FAMILY `sma_trend` has the best median holdout CAGR (19.6%) - add more parameters to it
- FAMILY `sma_trend_vol_filter` has the best median holdout CAGR (15.9%) - add more parameters to it
- FAMILY `sma_trend_efficiency` has the best median holdout CAGR (13.4%) - add more parameters to it
- FAMILY `ema_trend` has the best median holdout CAGR (10.6%) - add more parameters to it


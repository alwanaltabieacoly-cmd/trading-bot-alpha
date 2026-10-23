# Trading Bot

Bybit crypto trading bot with a **self-testing daily research harness**.

The system has two separate halves, on purpose:

| Half | What it does | Where it runs |
|---|---|---|
| **Research harness** (`research/`) | Fetches market data, backtests a library of strategies, validates them against overfitting, keeps track of a champion strategy | GitHub Actions, daily, works with this PC switched off |
| **Trading bot** (`user_data/`, Freqtrade) | Executes the champion strategy in paper trading | An always-on machine (this PC or a small VPS) |

The research half never places an order and never touches exchange
credentials. The trading half never changes the strategy on its own — it
runs whatever the research half has promoted.

---

## The strategy that actually worked

The rule is deliberately boring:

> **Hold the asset while `close` is above its 200-period SMA. Sit in cash otherwise.**

Measured on real Bybit data (2022-01-01 → 2026-10-18), with real costs
(0.1% Bybit taker fee + 0.02% slippage per side) and a one-bar signal delay
so there is no look-ahead:

| Asset (daily) | Strategy | Buy & hold | Strategy max DD | B&H max DD |
|---|---|---|---|---|
| BTC | **+243.8%** | +71.8% | **-31.8%** | -67.0% |
| ETH | **+131.1%** | -36.0% | **-38.4%** | -74.0% |
| SOL | **+220.6%** | -41.9% | **-58.6%** | -94.6% |

Average across 10 asset/timeframe combinations: **+109% vs +29%**, with a
smaller drawdown in **10 out of 10**.

Two things this test also proved, which is why they are in the rules:

- **Trading less beats trading more.** The same rule on the 1-hour
  timeframe loses money (-0.7% CAGR) because 1,400+ trades drown in fees.
- **Fast timeframes are not better.** Daily and 4-hourly work; hourly
  does not.

## Honest limits

- Long/cash only — there is no short side. In a pure bull run, buy and
  hold wins and this rule underperforms it.
- It loses on the strongest bull runners (BNB, XRP), because being in cash
  costs you the biggest rallies.
- The edge comes mostly from surviving the 2022 crash. In the bull-only
  2024–2026 window it is roughly a wash on return and better on drawdown.
- Past performance on one dataset is not a promise.

---

## The daily research harness

`research/run_daily.py` runs on a schedule and does this:

1. Fetch fresh Bybit candles and update the local cache.
2. Backtest **every** candidate in the strategy registry on the **train
   window** (everything up to the rolling split point).
3. Filter by the promotion rules.
4. Score survivors on the **holdout window** — the most recent 180 days,
   which the search never saw.
5. Apply the **Deflated Sharpe Ratio** correction for how many candidates
   were tried.
6. Re-evaluate the current champion on the same window.
7. Compare the best survivor to the champion.
8. Write a timestamped report and update the champion state.

### The split rolls forward

The holdout is **always the most recent 180 days**, and the split point
moves on every run. That is deliberate. The harness runs every 4 hours,
so with a fixed holdout a strategy could slowly "learn" the holdout just
by being examined over and over. With a rolling window, every run tests
against a stretch of data that was genuinely unseen when the selection was
made.

### Why it will not fool itself

A backtest that searches many parameter sets always finds something that
looks great. That is a property of the search, not of the market. Three
guards prevent the harness from promoting a curve-fit:

- **The holdout window is sacred.** Candidates are selected using train
  data only. Holdout is used solely to give a final verdict on the few
  survivors, never to choose between them.
- **Deflated Sharpe Ratio** (Lo, *The Statistics of Sharpe Ratios*).
  The Sharpe of the best of N trials is inflated by chance; the DSR
  subtracts that expectation. Without it, searching 76 parameter sets
  always "discovers" a winner.
- **Consistency.** A real edge shows up across assets. A lucky parameter
  set shows up on one and nowhere else. A candidate must work on at least
  3 of 5 assets.

On top of that, **nothing is promoted on backtest alone.** A challenger
becomes a *challenger* and must confirm itself in live paper trading
before it becomes the champion.

The state file also keeps a **cumulative count of every candidate ever
tested**. The Deflated Sharpe correction inside a single run only accounts
for that run's trials; the cumulative counter is the honest record of how
many times the whole search has been repeated over time.

### Running it

```bash
pip install ccxt pandas numpy pyarrow
python -m research.run_daily              # fetch fresh data and run
python -m research.run_daily --no-fetch   # use the cached data
```

Output lands in `research/reports/YYYY-MM-DD_HHMM.{json,md}` and the
champion state in `research/state/champion.json`.

### The strategy library

`research/strategies.py` holds the searchable space. It is small and
readable on purpose — a small, explicit space cannot hide a curve-fit:

| Strategy | Rule |
|---|---|
| `sma_trend` | close > SMA(n) |
| `ema_trend` | EMA(fast) > EMA(slow) |
| `donchian_trend` | close at the n-bar high |
| `sma_trend_vol_filter` | trend filter + stand aside when volatility spikes |
| `sma_trend_rsi_filter` | trend filter + overbought guard |
| `sma_trend_fast_slow` | trend filter + pullback recovery entry |
| `ema_trend_regime` | EMA cross with a volatility guard |
| `donchian_trend_vol_filter` | breakout trend with a volatility guard |

Adding a strategy means adding one function to this file. The harness
picks it up automatically.

---

## GitHub Actions — the only runner

`.github/workflows/strategy-research.yml` runs the harness **every 4 hours**
(00:17, 04:17, 08:17, 12:17, 16:17, 20:17 UTC) and commits the report and
champion state back to the repo. The history of runs is therefore the audit
trail.

**The project is designed to run entirely from GitHub.** This PC can be
switched off and nothing is lost:

- Each run starts on a fresh GitHub runner VM, does its work, commits, and
  the VM is destroyed. Between runs there is nothing running anywhere.
- The market data cache, the per-candidate history and every past report
  are committed to the repo, so a cold runner has the full history.
- Only four packages are needed on the runner: `ccxt`, `pandas`, `numpy`,
  `pyarrow`. No GPU, no model weights, no local install.

This was verified by cloning the repository into an empty directory,
building a fresh Python environment with only those four packages, and
running the full harness from there — it worked end to end.

The repository is **public on purpose**: GitHub Actions minutes are
unlimited on public repositories, so a 6x/day cadence costs nothing. There
are no secrets in it — every exchange credential field in `user_data/*.json`
is an empty string, and `config.private.json` is git-ignored.

The workflow only reads market data and writes reports. It has no exchange
credentials and cannot place an order.

## Running the trading bot

The Freqtrade side lives in `user_data/`. Bot configs are in
`user_data/bots/` (`botA.json`, `botB.json`, `botC.json`).

```bash
freqtrade trade --config user_data/bots/botA.json
```

Credentials live in `config.private.json`, which is **git-ignored** and
must never be committed.

> The paper-trading bot needs an always-on machine — this PC, or a small
> VPS. GitHub Actions runs the *research*, not the *trading*.

---

## What was tried and rejected

Kept here so the same dead ends are not re-explored:

| Idea | Result |
|---|---|
| TimesFM (Google's time-series foundation model) | No edge. Direction accuracy 45–60% against a 50% coin flip, no significant p-values on real Bybit data. |
| Kronos (financial foundation model) | Same story, and ~86s per forecast on CPU here. Installed at `D:\Openwork_Projects\ai-models`, parked. |
| Indicator combos (EMA/RSI crossovers) | No edge after fees, confirmed repeatedly. |
| FreqAI / ML regime classifiers | Negative on held-out 2022. |
| Multi-agent LLM debate (Bot B) | Agents blocked every decision; zero trades taken. |

The intelligence in this system comes from **robustness** — more assets,
more years, no look-ahead, real fees, statistical correction for the
number of trials — not from a bigger model.

---

## Vibe-Trading MCP (optional research power-up)

The repo ships a portable MCP config at `.mcp.json` that exposes
[Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) — 478 pre-built alphas,
11 backtest engines, factor analysis, options pricing, news/web research — to
any MCP-capable agent (Claude Code, opencode/Alphacode, Cursor).

```bash
pip install -r requirements-vibe.txt   # provides the `vibe-trading-mcp` command
```

The agent then gets `backtest`, `get_market_data`, `factor_analysis`,
`alpha_zoo`, `web_search`, `read_url` and 76 more tools. The core research
tools need **no API key** for US/HK/crypto data.

CI also runs a deterministic alpha benchmark every weekday
(`.github/workflows/vibe-research.yml`) and commits the report under
`research/reports/vibe/`. No LLM calls, no broker credentials, no orders.

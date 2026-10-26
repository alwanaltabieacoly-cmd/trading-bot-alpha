# Plan: daily crypto analyst + judge + learning loop on Gate (2026-10-26)

## Goal
An AI that reads the Gate crypto market every day, makes explicit calls with reasons, is scored honestly against what the market did, and lets the user learn from each call. No live money until the existing trade gate passes.

## What already exists (reuse, do not rebuild)
- Sessions 03:00 / 09:00 / 14:00 / 15:00 Tripoli: PC tasks + GitHub workflows from `config/sessions.json`.
- Pipeline: warmup -> deliberate (analyst, risk, critic, synthesizer, auditor) -> outcome labelling -> daily learning -> `feed/edge.py` honest stats -> digest `LATEST.md`.
- Trade gate: n>=30 independent calls, 95% lower bound >50%, beats always-long, GO net of costs. Status: NOT PROVEN (n=22).
- Paper trader `alpha/trader.py` with hard limits (2% stop, 2% size, 3 open, daily loss cap).

## Gaps found
1. **Universe.** The judge scores ~14 symbols from Yahoo. Gate crypto (33 liquid perps, plus XAU/XAG) is not scored. The user trades Gate.
2. **Horizon.** Outcomes are labelled at one daily horizon. Short-term ideas (hours) are never judged.
3. **Fill realism.** Paper trades use last price. Real trades pay the spread, walk the book and pay 0.10% (spot) / 0.02-0.05% (futures).
4. **Reasons are not machine-scored.** Calls carry prose, so we cannot tell which reason (trend, funding, liquidity sweep, imbalance) is right more often.
5. **Learning view.** No single page tells the user: what was chosen, why, what happened, what to change.
6. **Secrecy.** The repo is public. Account data, balances and journals must not go there.

## Build, in order
1. **Gate analyst** (`research/gate_analyst.py`, runs at each session, public data only):
   for every liquid Gate perp compute trend (SMA20/50/200), RSI, ATR%, relative strength vs BTC, funding, spread, book imbalance (from the logger), and write one structured call per coin:
   `{ts, coin, call: long|short|flat, horizon: 4h|24h|7d, entry, stop, target, reasons: [tags], score}`. Reason tags are a fixed list so they can be scored.
2. **Judge** (`research/gate_judge.py`): for each call, wait out its horizon, fetch Gate candles, resolve stop/target/timeout (stop first), subtract round-trip cost, one count per coin per candle. Report accuracy and net expectancy with 95% interval **per reason tag, per coin, per horizon**, against three baselines: always-long, random direction, SMA200 rule. Reuse `feed/edge.py` statistics.
3. **Book-walking paper fills**: price paper entries/exits from the logged Gate order book (buy at ask side depth, sell at bid), include fees. This is what makes paper results transferable to real trading.
4. **Daily review page** (`research/private/REVIEW_<date>.md`): each call with its reasons, the outcome, which reasons helped or hurt, plus a 10-line "what we learned". This is the page the user reads to learn why the AI chose something.
5. **Promotion ladder**, each step needs the previous to pass the gate for a given reason/coin/horizon cell:
   paper -> Gate futures testnet -> live with a hard cap (e.g. $20, 1 position, stop mandatory, trade-only API key with no withdrawal) -> scale only on live results.

## What counts as proof
- A reason tag or setup is trusted only with n>=30 independent calls, lower bound >50% **and** positive mean net of costs, and it must hold in two separate time halves.
- Multiple-testing rule: the number of reason/coin/horizon cells tested is logged; with ~100 cells expect ~5 false positives at 95%, so require the cell to also hold out-of-sample on the next 30 calls.
- Expected timeline: 30 independent calls per coin at 3 sessions/day takes about 10 days for the whole universe, much longer for any single cell. Plan for 4-6 weeks before any live decision.

## Secrecy
- GitHub repo `trading-bot` is public. It holds code and market-only research. It must never hold balances, trades, keys or the review pages.
- Private data stays in `research/private/` (gitignored). Backup option: a second **private** repo used only for storage (no Actions, so no minutes cost). Needs the user to create it.
- Gate key stays in Windows Credential Manager. GitHub Actions never gets the key. Public market data works without it (Actions reaching Gate from GitHub IPs: unverified).

## Limits to be honest about
- The AI brain is a free model; it can summarise and apply rules but cannot out-think the data. The edge, if any, comes from the measured rules and the judge, not from model cleverness.
- Candle and indicator rules tested so far (sections 15-17) show no edge after costs. This plan is the machine that finds out if anything does, and says so when nothing does.
- Past testing covered 7-day (1m) and ~800-day (daily) samples only; both can mislead.

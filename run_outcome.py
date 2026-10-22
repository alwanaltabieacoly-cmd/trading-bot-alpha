#!/usr/bin/env python3
"""End-of-day outcome tracker.

Compares the morning warmup GO/NO-GO verdict against what actually
happened during the trading day. Writes to reports/warmup/outcome_log.jsonl.

This is the feedback loop: record the prediction, check it later,
accumulate evidence about whether the warmup signal has real edge.

Usage:
    python run_outcome.py              # crypto pairs
    python run_outcome.py --all        # crypto + AAPL
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from research import config, data


def _find_latest_warmup():
    """Find the most recent warmup report for today."""
    wdir = os.path.join(config.REPORT_DIR, "warmup")
    if not os.path.isdir(wdir):
        return None
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    files = sorted(
        [f for f in os.listdir(wdir) if f.startswith(today) and f.endswith(".json")],
        reverse=True,
    )
    if not files:
        return None
    with open(os.path.join(wdir, files[0])) as f:
        return json.load(f)


def _price_change(symbol, tf, asof):
    """Get close-to-close price change for the day.

    Falls back through timeframes (1h -> 4h -> 1d) so the outcome tracker
    works even when a given bar size isn't cached.
    """
    import pandas as pd
    for tf_attempt in (tf, "4h", "1d"):
        df = data.load(symbol, tf_attempt)
        if df is None or len(df) < 2:
            continue
        asof_ts = pd.Timestamp(asof)
        df = df[df["date"] < asof_ts]
        if len(df) < 2:
            continue
        prior = float(df["close"].iloc[-2])
        last = float(df["close"].iloc[-1])
        if prior <= 0:
            continue
        return (last - prior) / prior * 100.0, last
    return None, None


def run(pairs, equity_symbols=None, asof=None):
    """Compare warmup verdicts to actual price moves."""

    equity_symbols = equity_symbols or []
    asof_dt = datetime.now(timezone.utc)
    asof_iso = config.now_iso()

    warmup = _find_latest_warmup()
    if not warmup:
        print("No warmup report found for today. Run run_warmup.py first.")
        return 1

    first = next(iter(warmup.values()), {})
    print(f"Warmup from: {first.get('asof', 'unknown')}")

    outcomes = []
    for pair in pairs:
        w = warmup.get(pair, {})
        verdict = w.get("verdict", "UNKNOWN")
        score = w.get("score", 0)

        symbol = pair.replace("/USDT", "")
        tf = "1h"
        chg, last_price = _price_change(symbol, tf, asof_iso)

        # Did the warmup call it right?
        if chg is None:
            result = "NO_DATA"
        elif verdict == "GO" and chg > 0:
            result = "CORRECT"
        elif verdict == "GO" and chg <= 0:
            result = "WRONG"
        elif verdict == "NO-GO" and chg < 0:
            result = "CORRECT"
        elif verdict == "NO-GO" and chg >= 0:
            result = "MISSED"
        else:
            result = "UNKNOWN"

        outcomes.append({
            "pair": pair,
            "verdict": verdict,
            "score": score,
            "price_change_1h_pct": chg,
            "last_price": last_price,
            "result": result,
        })
        print(f"  {pair:12s} warmup={verdict:5s} score={score:3d}  "
              f"1h chg={chg if chg is not None else 'N/A':>7}%  -> {result}")

    for sym in equity_symbols:
        w = warmup.get(sym, {})
        verdict = w.get("verdict", "UNKNOWN")
        score = w.get("score", 0)
        chg, last_price = _price_change(sym, "1d", asof_iso)
        if chg is None:
            result = "NO_DATA"
        elif verdict == "GO" and chg > 0:
            result = "CORRECT"
        elif verdict == "GO" and chg <= 0:
            result = "WRONG"
        elif verdict == "NO-GO" and chg < 0:
            result = "CORRECT"
        elif verdict == "NO-GO" and chg >= 0:
            result = "MISSED"
        else:
            result = "UNKNOWN"
        outcomes.append({
            "pair": sym,
            "verdict": verdict,
            "score": score,
            "price_change_1d_pct": chg,
            "last_price": last_price,
            "result": result,
        })
        print(f"  {sym:12s} warmup={verdict:5s} score={score:3d}  "
              f"1d chg={chg if chg is not None else 'N/A':>7}%  -> {result}")

    # Write to outcome log
    wdir = os.path.join(config.REPORT_DIR, "warmup")
    os.makedirs(wdir, exist_ok=True)
    log = os.path.join(wdir, "outcome_log.jsonl")
    record = {"ts": asof_iso, "outcomes": outcomes}
    with open(log, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")
    print(f"\nAppended to {log}")

    # Running summary
    correct = sum(1 for o in outcomes if o["result"] == "CORRECT")
    wrong = sum(1 for o in outcomes if o["result"] == "WRONG")
    missed = sum(1 for o in outcomes if o["result"] == "MISSED")
    total = len(outcomes)
    if total > 0:
        print(f"Today: {correct} correct, {wrong} wrong, {missed} missed "
              f"({correct/total*100:.0f}% accuracy)")
    return 0


if __name__ == "__main__":
    pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    equity = []
    if "--all" in sys.argv:
        equity = ["AAPL"]
    sys.exit(run(pairs, equity_symbols=equity))

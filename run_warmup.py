#!/usr/bin/env python3
"""Daily pre-trade warmup: Trade Agent reads news + market + deliberation
before any paper or live trading begins.

Runs every market day ~15 min before the US open (14:45 UTC = 9:45 AM ET).
Writes a timestamped report to reports/warmup/ and appends to a running log.

Usage:
    python run_warmup.py                    # crypto pairs
    python run_warmup.py --equity AAPL      # add equity
    python run_warmup.py --all              # crypto + AAPL
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import trade_agent
from research import config

CRYPTO_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
EQUITY_SYMBOLS = ["AAPL"]


def run(pairs, equity_symbols=None, asof=None):
    equity_symbols = equity_symbols or []
    results = {}
    for pair in pairs:
        print(f"\n--- {pair} ---")
        r = trade_agent.warmup(pair, equity=False, asof=asof)
        results[pair] = r
        print(f"  Verdict: {r['verdict']} (score={r['score']})")
        if r['blockers']:
            for b in r['blockers']:
                print(f"    BLOCK: {b}")
    for sym in equity_symbols:
        print(f"\n--- {sym} (equity) ---")
        r = trade_agent.warmup(sym, equity=True, asof=asof)
        results[sym] = r
        print(f"  Verdict: {r['verdict']} (score={r['score']})")
        if r['blockers']:
            for b in r['blockers']:
                print(f"    BLOCK: {b}")

    # Write report
    wdir = os.path.join(config.REPORT_DIR, "warmup")
    os.makedirs(wdir, exist_ok=True)
    ts = (datetime.now(timezone.utc)).strftime("%Y-%m-%d_%H%M")
    out = os.path.join(wdir, f"{ts}.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nWrote {out}")

    # Running log
    log = os.path.join(wdir, "warmup_log.jsonl")
    with open(log, "a") as f:
        f.write(json.dumps({"ts": ts, "results": results}, default=str) + "\n")
    return results


if __name__ == "__main__":
    pairs = list(CRYPTO_PAIRS)
    equity = []
    if "--all" in sys.argv:
        equity = list(EQUITY_SYMBOLS)
    if "--equity" in sys.argv:
        idx = sys.argv.index("--equity")
        equity = sys.argv[idx + 1].split(",")
    run(pairs, equity_symbols=equity)

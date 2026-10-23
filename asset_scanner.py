#!/usr/bin/env python3
"""Scan many crypto pairs and rank them by warmup score + profitability.

The warmup currently watches BTC, ETH, SOL and AAPL. This module expands
the universe: it fetches a candidate list from Kraken, runs the feature
engine on each, and ranks by expected profitability -- not just GO/NO-GO
but which pairs have the strongest micro-structure edge.

Usage:
    python asset_scanner.py              # scan Kraken spot pairs
    python asset_scanner.py --top 10     # show top 10
    python asset_scanner.py --json       # machine-readable output
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from agents import common, feature_engine
from research import config

# Default universe: Kraken spot pairs worth watching.
# We start with majors + mid-caps that have real volume.
DEFAULT_PAIRS = [
    "BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX", "LINK",
    "DOT", "MATIC", "LTC", "BCH", "UNI", "ATOM", "XLM", "NEAR",
    "ALGO", "FIL", "ICP", "APT", "ARB", "OP", "SAND", "MANA",
    "SHIB", "PEPE", "INJ", "TIA", "JTO", "PEN", "GALA", "AXS",
]


def _fetch_kraken_pairs():
    """Get the list of tradable USD pairs from Kraken."""
    try:
        import ccxt
        ex = ccxt.kraken({"enableRateLimit": True})
        markets = ex.load_markets()
        pairs = []
        for symbol, m in markets.items():
            if not m.get("active"):
                continue
            base = symbol.split("/")[0]
            quote = symbol.split("/")[1] if "/" in symbol else ""
            if quote in ("USD", "USDT") and base not in ("USD", "USDT"):
                pairs.append(base)
        return sorted(set(pairs))
    except Exception as e:
        print(f"Kraken market fetch failed: {e}")
        return DEFAULT_PAIRS


def _score_pair(base, tf="1h"):
    """Run the feature engine on a pair and return a profitability score."""
    df = common.load_candles(f"{base}/USD", tf, None)
    if df is None or len(df) < 20:
        return None
    feats = feature_engine.extract(df, f"{base}/USD", tf)
    if not feats:
        return None
    mom = feats["momentum_3_5_10_21"]
    micro = feats["micro_score"]
    vol = feats["vol_regime"]
    vspike = feats["volume_spike"]
    pos = feats["candle_position"]
    close = feats["last_close"]

    # Expected profitability: momentum + micro-structure + position
    # Positive momentum + absorption + near support = highest score
    score = mom * 2.0 + micro * 3.0 + vol * 1.5 + vspike * 2.0 + pos * 2.0
    return {
        "pair": f"{base}/USD",
        "close": close,
        "momentum": round(mom, 4),
        "micro_score": round(micro, 4),
        "vol_regime": round(vol, 3),
        "volume_spike": round(vspike, 3),
        "candle_position": round(pos, 3),
        "profit_score": round(score, 4),
    }


def run(pairs=None, top_n=10, as_json=False, max_pairs=20):
    if pairs is None:
        pairs = _fetch_kraken_pairs()
    pairs = pairs[:max_pairs]
    print(f"Scanning {len(pairs)} pairs from Kraken...")

    results = []
    for i, base in enumerate(pairs):
        if (i + 1) % 10 == 0:
            print(f"  ... {i+1}/{len(pairs)}")
        try:
            r = _score_pair(base)
            if r:
                results.append(r)
        except Exception:
            continue

    results.sort(key=lambda r: r["profit_score"], reverse=True)

    print(f"\n=== TOP {top_n} PAIRS BY PROFITABILITY ===")
    for i, r in enumerate(results[:top_n]):
        print(f"#{i+1} {r['pair']:12s} score={r['profit_score']:+.4f}  "
              f"mom={r['momentum']:+.4f}  micro={r['micro_score']:+.4f}  "
              f"vol={r['vol_regime']:+.3f}  close={r['close']}")

    if as_json:
        print(json.dumps(results[:top_n], indent=2, default=str))
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", default=None)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    run(pairs=args.pairs, top_n=args.top, as_json=args.json)

#!/usr/bin/env python3
"""Probe the external data sources we depend on. Never raises; writes health.

Why: Yahoo/Kraken/OKX can break, geo-block, or rate-limit. Silent breakage is
what hurts, so each source gets a tiny, time-bounded probe and the result is
committed. system_check.py reads this file and goes red if every source is down.

Usage:
    python scripts/source_health.py --write
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT_PATH = ROOT / "research" / "reports" / "health" / "sources.json"
TIMEOUT_MS = 15000


def _probe_ccxt(exchange_name, symbol):
    import ccxt
    ex = getattr(ccxt, exchange_name)({"enableRateLimit": True, "timeout": TIMEOUT_MS})
    rows = ex.fetch_ohlcv(symbol, timeframe="1d", limit=5)
    if not rows:
        raise RuntimeError("empty candles")
    return {"rows": len(rows), "last_close": float(rows[-1][4])}


def _probe_yahoo(symbol="AAPL"):
    from research import data
    frame = data.fetch_equity_candles(symbol, "1d", days_back=10)
    if frame is None or len(frame) == 0:
        raise RuntimeError("no rows")
    return {"rows": int(len(frame)), "last_close": float(frame["close"].iloc[-1])}


PROBES = (
    ("kraken", lambda: _probe_ccxt("kraken", "BTC/USD")),
    ("okx", lambda: _probe_ccxt("okx", "BTC/USDT")),
    ("yahoo", _probe_yahoo),
)


def run(now=None):
    now = now or datetime.now(timezone.utc)
    results = {}
    for name, probe in PROBES:
        start = time.time()
        try:
            detail = probe()
            results[name] = {"ok": True, "latency_ms": int((time.time() - start) * 1000), **detail}
        except Exception as e:
            results[name] = {"ok": False, "latency_ms": int((time.time() - start) * 1000),
                             "error": f"{type(e).__name__}: {str(e)[:140]}"}
    return {
        "generated_at": now.isoformat(),
        "all_ok": all(r["ok"] for r in results.values()),
        "any_ok": any(r["ok"] for r in results.values()),
        "sources": results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scripts/source_health.py")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--summary", action="store_true",
                        help="print a one-line summary of the last written report")
    args = parser.parse_args(argv)

    if args.summary:
        try:
            report = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print("sources: no report yet")
            return 0
        flags = {name: item.get("ok") for name, item in report.get("sources", {}).items()}
        print(f"sources: {flags}")
        return 0

    report = run()
    if args.write:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"wrote {OUT_PATH}")
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["any_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Pick deliberation candidates from the latest multi-asset scan.

Rules (deliberately boring):
  - only rows with a POSITIVE profit_score are eligible;
  - per-class quota: 3 crypto, 2 equities, 1 FX (all overridable);
  - output the decision-symbol spelling used by deliberation/evidence
    (BTC/USDT, AAPL, EURUSD).

The deliberate workflow calls ``--print`` when no explicit pairs were given.
An empty selection prints nothing, and the workflow falls back to its default
pairs -- the shortlist is an optimisation, never a hard dependency.

Usage:
    python scripts/scan_shortlist.py --print
    python scripts/scan_shortlist.py --crypto 4 --equity 3 --forex 1
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents import universe  # noqa: E402

SCAN_PATH = ROOT / "research" / "reports" / "asset_scan.json"
OUT_PATH = ROOT / "research" / "reports" / "scan_shortlist.json"
DEFAULT_QUOTA = {"crypto": 3, "equity": 2, "forex": 1}
MIN_SCORE = 0.0


def _class_of(row):
    cls = row.get("asset_class")
    if cls in ("crypto", "equity", "forex"):
        return cls
    return universe.classify(row.get("pair", "")) or "crypto"


def select(rows, quota=None, min_score=MIN_SCORE):
    """Return shortlist picks: highest score per class, quota-capped."""
    quota = quota or DEFAULT_QUOTA
    picks = []
    for cls, limit in quota.items():
        group = [
            row for row in rows
            if isinstance(row, dict)
            and _class_of(row) == cls
            and isinstance(row.get("profit_score"), (int, float))
            and row["profit_score"] > min_score
        ]
        group.sort(key=lambda row: row["profit_score"], reverse=True)
        for row in group[:limit]:
            picks.append({
                "symbol": row.get("pair"),
                "decision_symbol": universe.decision_symbol(row.get("pair", "")),
                "asset_class": cls,
                "profit_score": row.get("profit_score"),
                "momentum": row.get("momentum"),
                "micro_score": row.get("micro_score"),
            })
    picks.sort(key=lambda item: item["profit_score"], reverse=True)
    return picks


def load_scan(path=None):
    path = Path(path or SCAN_PATH)
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return rows if isinstance(rows, list) else []


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scripts/scan_shortlist.py")
    parser.add_argument("--scan", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--crypto", type=int, default=DEFAULT_QUOTA["crypto"])
    parser.add_argument("--equity", type=int, default=DEFAULT_QUOTA["equity"])
    parser.add_argument("--forex", type=int, default=DEFAULT_QUOTA["forex"])
    parser.add_argument("--min-score", type=float, default=MIN_SCORE)
    parser.add_argument("--print", action="store_true",
                        help="print comma-separated decision symbols (for the workflow)")
    args = parser.parse_args(argv)

    quota = {"crypto": args.crypto, "equity": args.equity, "forex": args.forex}
    picks = select(load_scan(args.scan), quota=quota, min_score=args.min_score)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "min_score": args.min_score,
        "quota": quota,
        "picks": picks,
        "decision_pairs": [p["decision_symbol"] for p in picks],
    }
    out_path = Path(args.out or OUT_PATH)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    if args.print:
        print(",".join(payload["decision_pairs"]))
    else:
        print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

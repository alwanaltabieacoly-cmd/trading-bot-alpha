"""Data-quality audit: is the data we trade on real, fresh and complete?

The gate blocks on stale *decisions*; this checks the raw bars underneath them.
Every cached symbol is scored on four things a trader actually cares about:

  bars      enough history for the features/warmup to mean something
  gaps      bars present vs bars expected for the calendar span
  staleness age of the newest bar at run time
  volume    share of zero-volume bars (normal for FX via Yahoo; suspicious elsewhere)

Verdicts: ok | warn | bad. Nothing here is fatal by itself -- the audit reports
and the brief repeats the warnings, so a decision is never made on silence.

Usage:
    python scripts/data_quality.py --write      # writes research/reports/quality/data_quality.json
    python scripts/data_quality.py              # prints JSON + markdown summary
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents import universe  # noqa: E402

OUT_DIR = ROOT / "research" / "reports" / "quality"
MIN_BARS = {"crypto": 300, "equity": 120, "forex": 120}
# Expected bars per calendar day, and how stale a newest bar may be.
BARS_PER_DAY = {"crypto": 6, "equity": 5 / 7, "forex": 5 / 7}
MAX_STALE_HOURS = {"crypto": 12.0, "equity": 96.0, "forex": 96.0}
GAP_WARN = 0.15
GAP_BAD = 0.40
ZERO_VOL_WARN = 0.95


def _load_frame(symbol, asset_class):
    """Scan/universe cache first, then the committed research cache."""
    from agents import common

    frame = universe.load(symbol)
    if frame is not None and len(frame):
        return frame
    pair = universe.decision_symbol(symbol) if asset_class == "crypto" else universe.display_symbol(symbol)
    return common.load_candles(pair, universe.DEFAULT_TF[asset_class], None)


def _audit_symbol(symbol, asset_class, now):
    frame = _load_frame(symbol, asset_class)
    tf = universe.DEFAULT_TF[asset_class]
    if frame is None or len(frame) == 0:
        return {
            "symbol": universe.display_symbol(symbol),
            "asset_class": asset_class,
            "tf": tf,
            "verdict": "bad",
            "reason": "no cached data",
            "bars": 0,
        }
    first = frame["date"].iloc[0]
    last = frame["date"].iloc[-1]
    span_days = max((last - first).total_seconds() / 86400.0, 0.0)
    expected = max(span_days * BARS_PER_DAY[asset_class], 1.0)
    gap_ratio = round(max(0.0, 1.0 - len(frame) / expected), 3)
    stale_hours = round((now - last).total_seconds() / 3600.0, 1)
    volume = frame["volume"]
    zero_share = round(float((volume <= 0).mean()), 3) if len(volume) else None

    reasons = []
    verdict = "ok"
    if len(frame) < MIN_BARS[asset_class]:
        reasons.append(f"only {len(frame)} bars (< {MIN_BARS[asset_class]})")
        verdict = "bad"
    if gap_ratio > GAP_BAD:
        reasons.append(f"gap ratio {gap_ratio:.0%}")
        verdict = "bad"
    elif gap_ratio > GAP_WARN and verdict != "bad":
        reasons.append(f"gap ratio {gap_ratio:.0%}")
        verdict = "warn"
    if stale_hours > MAX_STALE_HOURS[asset_class]:
        reasons.append(f"stale {stale_hours:.0f}h")
        verdict = "bad" if stale_hours > MAX_STALE_HOURS[asset_class] * 3 else "warn"
    if zero_share is not None and zero_share > ZERO_VOL_WARN and asset_class != "forex":
        reasons.append(f"zero-volume bars {zero_share:.0%}")
        if verdict == "ok":
            verdict = "warn"

    return {
        "symbol": universe.display_symbol(symbol),
        "asset_class": asset_class,
        "tf": tf,
        "verdict": verdict,
        "reason": "; ".join(reasons) or "ok",
        "bars": int(len(frame)),
        "span_days": round(span_days, 1),
        "gap_ratio": gap_ratio,
        "stale_hours": stale_hours,
        "zero_volume_share": zero_share,
        "first_bar": first.isoformat(),
        "last_bar": last.isoformat(),
    }


def audit(limit=None, now=None):
    now = now or datetime.now(timezone.utc)
    rows = []
    for asset_class in ("crypto", "equity", "forex"):
        for symbol in universe.watchlist(asset_class, limit):
            rows.append(_audit_symbol(symbol, asset_class, now))
    counts = {"ok": 0, "warn": 0, "bad": 0}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    by_class = {}
    for asset_class in ("crypto", "equity", "forex"):
        group = [r for r in rows if r["asset_class"] == asset_class]
        by_class[asset_class] = {
            "total": len(group),
            "ok": sum(1 for r in group if r["verdict"] == "ok"),
            "warn": sum(1 for r in group if r["verdict"] == "warn"),
            "bad": sum(1 for r in group if r["verdict"] == "bad"),
        }
    return {
        "generated_at": now.isoformat(),
        "counts": counts,
        "by_class": by_class,
        "symbols": rows,
    }


def markdown(report, worst=6):
    counts = report["counts"]
    lines = ["## Data quality", ""]
    lines.append(f"ok **{counts.get('ok', 0)}** · warn **{counts.get('warn', 0)}** · bad **{counts.get('bad', 0)}**")
    lines.append("")
    for asset_class, item in report["by_class"].items():
        lines.append(f"- {asset_class}: {item['ok']}/{item['total']} ok"
                     + (f", {item['warn']} warn" if item["warn"] else "")
                     + (f", {item['bad']} bad" if item["bad"] else ""))
    bad = [r for r in report["symbols"] if r["verdict"] != "ok"]
    if bad:
        lines.append("")
        lines.append("| symbol | class | verdict | bars | gaps | stale | reason |")
        lines.append("|---|---|---|---|---|---|---|")
        for row in bad[:worst]:
            lines.append(
                f"| {row['symbol']} | {row['asset_class']} | {row['verdict']} | {row['bars']} | "
                f"{row.get('gap_ratio', '-')} | {row.get('stale_hours', '-')}h | {row['reason']} |"
            )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scripts/data_quality.py")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    report = audit(limit=args.limit)
    if args.write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / "data_quality.json"
        path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"wrote {path}")
    print(json.dumps(report["counts"], indent=2))
    print(markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())

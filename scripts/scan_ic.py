#!/usr/bin/env python3
"""Does the scan score actually predict? The scanner's information coefficient.

This is the honest test of our own signal: at many historical timestamps,
compute each symbol's scan score (using only data available then), then measure
the rank correlation between those scores and the next-period return across
symbols. That is the standard cross-sectional IC / IR test.

Verdict (written to the artifact, not hidden):
    predictive   ic_mean > 0.02 and ir > 0.15 with >= 20 snapshots
    weak         ic_mean > 0
    no-evidence  otherwise
    insufficient not enough data yet

Usage:
    python scripts/scan_ic.py --write
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents import common, feature_engine, universe  # noqa: E402

OUT_JSON = ROOT / "research" / "reports" / "scan_ic.json"
OUT_MD = ROOT / "research" / "reports" / "scan_ic.md"

# class -> (tf, horizon bars, snapshot step bars, max snapshots, min symbols)
SETTINGS = {
    "crypto": ("4h", 6, 6, 60, 6),
    "equity": ("1d", 1, 1, 120, 6),
    "forex": ("1d", 1, 1, 120, 5),
}
MIN_BARS = 40


def spearman(a, b):
    """Rank correlation without scipy; None when undefined."""
    if len(a) != len(b) or len(a) < 3:
        return None
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.std(ra) == 0 or np.std(rb) == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def score_at(df, tf):
    """Scan score using only bars up to the end of this frame."""
    feats = feature_engine.extract(df, "panel", tf)
    if not feats:
        return None
    return (feats["momentum_3_5_10_21"] * 2.0 + feats["micro_score"] * 3.0
            + feats["vol_regime"] * 1.5 + feats["volume_spike"] * 2.0
            + feats["candle_position"] * 2.0)


def _load_class(asset_class):
    tf = SETTINGS[asset_class][0]
    out = {}
    for symbol in universe.watchlist(asset_class):
        pair = universe.decision_symbol(symbol) if asset_class == "crypto" else universe.display_symbol(symbol)
        frame = None
        try:
            frame = common.load_candles(pair, tf, None)
        except Exception:
            frame = None
        if frame is None or len(frame) < MIN_BARS:
            continue
        cols = [c for c in ("date", "open", "high", "low", "close", "volume") if c in frame.columns]
        if len(cols) < 6:
            continue
        frame = frame[cols].dropna(subset=["close"]).sort_values("date").reset_index(drop=True)
        out[symbol] = frame
    return out


def snapshots(asset_class, data):
    """Yield (date, scores dict, forward returns dict) using only past data.

    The timestamp axis comes from the symbol with the longest history, not from
    the intersection of every symbol's dates. A global intersection collapses as
    soon as symbols have heterogeneous coverage (24 crypto pairs across six
    exchanges do), which silently produced zero snapshots in CI while the same
    code measured fine locally with fewer symbols. Each symbol still contributes
    only its own past bars, so there is no look-ahead: a symbol whose history
    starts after the stamp is simply skipped at that timestamp.
    """
    tf, horizon, step, max_snaps, min_symbols = SETTINGS[asset_class]
    if len(data) < min_symbols:
        return []
    provider = max(data, key=lambda s: len(data[s]))
    axis = sorted(set(pd.to_datetime(data[provider]["date"], utc=True)))
    if len(axis) < MIN_BARS + horizon + step:
        return []

    picked = []
    for t_index in range(MIN_BARS, len(axis) - horizon, step):
        stamp = axis[t_index]
        stamp_ts = pd.Timestamp(stamp)
        scores, forwards = {}, {}
        for symbol, frame in data.items():
            dates = pd.to_datetime(frame["date"], utc=True)
            pos = int(np.searchsorted(dates.astype("int64").to_numpy(), stamp_ts.value))
            if pos < MIN_BARS or pos + horizon >= len(frame):
                continue
            hist = frame.iloc[:pos]
            score = score_at(hist, tf)
            if score is None:
                continue
            close_now = float(frame["close"].iloc[pos])
            close_fwd = float(frame["close"].iloc[pos + horizon])
            if close_now <= 0:
                continue
            scores[symbol] = score
            forwards[symbol] = close_fwd / close_now - 1.0
        if len(scores) >= min_symbols:
            picked.append((stamp, scores, forwards))
    return picked[-max_snaps:]


def analyse(asset_class, data=None):
    data = _load_class(asset_class) if data is None else data
    rows = snapshots(asset_class, data)
    ics = []
    for _stamp, scores, forwards in rows:
        symbols = [s for s in scores if s in forwards]
        if len(symbols) < SETTINGS[asset_class][4]:
            continue
        ic = spearman([scores[s] for s in symbols], [forwards[s] for s in symbols])
        if ic is not None:
            ics.append(ic)
    n = len(ics)
    if n == 0:
        return {"status": "insufficient", "n_snapshots": 0, "n_symbols": len(data)}
    mean = float(np.mean(ics))
    std = float(np.std(ics, ddof=1)) if n > 1 else 0.0
    ir = float(mean / std) if std > 0 else None
    verdict = "no-evidence"
    if n >= 20 and mean > 0.02 and ir is not None and ir > 0.15:
        verdict = "predictive"
    elif mean > 0:
        verdict = "weak"
    return {
        "status": "ok",
        "verdict": verdict,
        "n_snapshots": n,
        "n_symbols": len(data),
        "ic_mean": round(mean, 5),
        "ic_std": round(std, 5),
        "ir": round(ir, 4) if ir is not None else None,
        "ic_positive_ratio": round(float(np.mean([1.0 if x > 0 else 0.0 for x in ics])), 3),
        "horizon_bars": SETTINGS[asset_class][1],
        "tf": SETTINGS[asset_class][0],
    }


def markdown(report):
    lines = ["# Scan information coefficient", ""]
    lines.append(f"generated: {report['generated_at']}")
    lines.append("")
    lines.append("| class | verdict | snapshots | symbols | IC mean | IR | IC+ ratio |")
    lines.append("|---|---|---|---|---|---|---|")
    for cls, row in report["classes"].items():
        lines.append(
            f"| {cls} | {row.get('verdict', row.get('status'))} | {row.get('n_snapshots')} | "
            f"{row.get('n_symbols')} | {row.get('ic_mean')} | {row.get('ir')} | "
            f"{row.get('ic_positive_ratio')} |"
        )
    lines += ["", "IC = rank correlation between the scan score and the next-period return,",
              "measured across symbols at many historical timestamps. Positive IC and IR > 0.15",
              "is the minimum honest evidence that the score carries information."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scripts/scan_ic.py")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--require-snapshots", action="store_true",
                        help="exit non-zero if any class measures zero snapshots. "
                             "Zero snapshots means the measurement is broken, not "
                             "that the signal has no evidence, so it must fail the "
                             "job rather than be recorded as 'insufficient'.")
    args = parser.parse_args(argv)
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "classes": {}}
    for asset_class in SETTINGS:
        try:
            report["classes"][asset_class] = analyse(asset_class)
        except Exception as e:
            report["classes"][asset_class] = {"status": "error",
                                              "error": f"{type(e).__name__}: {e}"}
    text = markdown(report)
    print(text)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        OUT_MD.write_text(text, encoding="utf-8")
        print(f"wrote {OUT_JSON}")

    # Fail closed: a class that measured zero snapshots is a broken measurement.
    if args.require_snapshots:
        broken = [c for c, r in report["classes"].items()
                  if r.get("n_snapshots", 0) == 0]
        if broken:
            print(f"REFUSING: zero snapshots for {broken} -- measurement is broken, "
                  f"not evidence-free", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

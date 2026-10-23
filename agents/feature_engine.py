"""Candle micro-structure feature engine.

The market agent used to compute 8 features per timeframe. This module
adds the details that actually move prices: body/wick ratios, momentum
at multiple horizons, volatility regimes, volume profiles, and candle
pattern recognition. Every number is computed from OHLCV.

The features feed a verdict/outcome store + weight tuner that improves
every day. Each warmup writes its verdict. Each outcome labels it
correct/missed/wrong. The tuner re-weights the scoring signals so the
system gets smarter and loses less over time.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from . import common

# Default scoring weights. The tuner adjusts these from outcome history.
WEIGHTS = {
    "regime_bull": 2.0,
    "regime_bear": -2.0,
    "fng_fear": 1.0,
    "fng_greed": -1.0,
    "gdelt_neg": -1.0,
    "deliberation_block": -3.0,
    "momentum_up": 1.5,
    "momentum_down": -1.5,
    "vol_squeeze": 1.0,
    "vol_expand": -0.5,
    "absorption": 1.0,
    "exhaustion": -1.0,
    "volume_spike": 1.0,
}

WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "user_data" / "feature_weights.json"


def load_weights():
    if WEIGHTS_PATH.exists():
        try:
            with open(WEIGHTS_PATH) as f:
                saved = json.load(f)
            merged = dict(WEIGHTS)
            merged.update(saved)
            return merged
        except Exception:
            pass
    return dict(WEIGHTS)


def save_weights(w):
    WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WEIGHTS_PATH, "w") as f:
        json.dump(w, f, indent=2)

# ---------------------------------------------------------------------------
# Candle micro-structure features.  All computed from raw OHLCV -- no
# black-box indicators.  Each returns a signed score contribution.
# ---------------------------------------------------------------------------

def _body_wick(df):
    """Body size and wick ratio for the last N candles.

    A long lower wick + small body = absorption (buyers stepping in).
    A long upper wick + small body = exhaustion (sellers winning).
    """
    n = min(len(df), 20)
    if n < 3:
        return 0.0, 0.0
    recent = df.iloc[-n:]
    body = (recent["close"] - recent["open"]).abs()
    rng = recent["high"] - recent["low"]
    rng = rng.replace(0, np.nan)
    body_ratio = (body / rng).fillna(0.5).mean()

    lower = (recent[["open", "close"]].min(axis=1) - recent["low"]).abs()
    upper = (recent["high"] - recent[["open", "close"]].max(axis=1)).abs()
    total_wick = (lower + upper).replace(0, np.nan)
    lower_ratio = (lower / total_wick).fillna(0.5).mean()

    # Absorption: long lower wicks, small bodies, price holding
    absorption = 0.0
    if body_ratio < 0.35 and lower_ratio > 0.55:
        absorption = 1.0
    # Exhaustion: long upper wicks, small bodies
    exhaustion = 0.0
    if body_ratio < 0.35 and lower_ratio < 0.45:
        exhaustion = -1.0
    return round(float(absorption), 3), round(float(exhaustion), 3)


def _momentum(df, horizons=(3, 5, 10, 21)):
    """Return-change at multiple horizons.  Multi-timeframe confirmation."""
    if len(df) < max(horizons) + 2:
        return 0.0
    close = df["close"]
    scores = []
    for h in horizons:
        if len(close) <= h:
            continue
        chg = (close.iloc[-1] - close.iloc[-1 - h]) / close.iloc[-1 - h]
        if pd.isna(chg):
            continue
        # Weight: shorter horizons matter more for scalps
        w = 1.0 / (h ** 0.5)
        scores.append(float(chg) * w)
    if not scores:
        return 0.0
    return round(float(np.mean(scores)) * 100.0, 4)


def _vol_regime(df, window=20):
    """Is volatility expanding or in a squeeze?"""
    if len(df) < window + 5:
        return 0.0
    high = df["high"]
    low = df["low"]
    recent_range = (high.iloc[-window:] - low.iloc[-window:]).mean()
    prior_range = (high.iloc[-2 * window:-window] - low.iloc[-2 * window:-window]).mean()
    if prior_range <= 0 or pd.isna(prior_range):
        return 0.0
    ratio = recent_range / prior_range
    if ratio > 1.6:
        return -0.5   # volatility expanding -- risky
    if ratio < 0.6:
        return 1.0    # volatility squeeze -- breakout pending
    return 0.0


def _volume_profile(df, window=20):
    """Where volume is concentrated -- accumulation or distribution."""
    if len(df) < window + 3:
        return 0.0
    recent = df.iloc[-window:]
    vol = recent["volume"]
    price_change = recent["close"].iloc[-1] - recent["close"].iloc[0]
    avg_vol = vol.mean()
    if avg_vol <= 0:
        return 0.0
    last_vol = vol.iloc[-1]
    vol_ratio = last_vol / avg_vol
    spike = 0.0
    if vol_ratio > 2.0:
        spike = 1.0 if price_change > 0 else -1.0
    return round(float(spike), 3)


def _candle_position(df, window=20):
    """Where the close sits within the recent range -- exhaustion or continuation."""
    if len(df) < window:
        return 0.0
    high = df["high"].iloc[-window:].max()
    low = df["low"].iloc[-window:].min()
    last_close = df["close"].iloc[-1]
    if high <= low:
        return 0.0
    pos = (last_close - low) / (high - low)
    if pos > 0.9:
        return -0.5   # near resistance
    if pos < 0.1:
        return 0.5    # near support
    return 0.0


def extract(df, pair, tf):
    """Extract the full feature vector from a candle DataFrame.

    Returns a dict of named features plus a combined micro_score.
    """
    if df is None or len(df) < 5:
        return None

    absorption, exhaustion = _body_wick(df)
    momentum = _momentum(df)
    vol = _vol_regime(df)
    vol_spike = _volume_profile(df)
    position = _candle_position(df)

    micro = (
        absorption
        + exhaustion
        + momentum * 0.05
        + vol
        + vol_spike
        + position
    )

    return {
        "tf": tf,
        "body_absorption": absorption,
        "body_exhaustion": exhaustion,
        "momentum_3_5_10_21": round(momentum, 4),
        "vol_regime": round(vol, 3),
        "volume_spike": vol_spike,
        "candle_position": round(position, 3),
        "micro_score": round(micro, 4),
        "n_bars": int(len(df)),
        "last_close": round(float(df["close"].iloc[-1]), 4),
    }


# ---------------------------------------------------------------------------
# Verdict / outcome store.  Every warmup writes a verdict.  Every outcome
# labels it correct/missed/wrong.  The tuner reads the history and adjusts
# the scoring weights so the system learns which signals actually work.
# ---------------------------------------------------------------------------

OUTCOME_DIR = Path(__file__).resolve().parent.parent / "research" / "reports" / "verdicts"
OUTCOME_LOG = OUTCOME_DIR / "outcome_log.jsonl"


def record_verdict(pair, features, score, verdict, blockers, weights_used):
    """Write a warmup verdict with the full feature vector attached."""
    OUTCOME_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "pair": pair,
        "features": features,
        "score": score,
        "verdict": verdict,
        "blockers": blockers,
        "weights": weights_used,
    }
    with open(OUTCOME_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{pair.replace('/', '_')}.json", "w") as f:
        json.dump(rec, f, indent=2, default=str)
    with open(OUTCOME_LOG, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    return rec


def record_outcome(pair, verdict, price_change_pct, result):
    """Label a past verdict as CORRECT / MISSED / WRONG."""
    OUTCOME_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "pair": pair,
        "verdict": verdict,
        "price_change_pct": price_change_pct,
        "result": result,
    }
    with open(OUTCOME_LOG, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    return rec


def _load_history():
    if not OUTCOME_LOG.exists():
        return []
    rows = []
    with open(OUTCOME_LOG) as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def tune_weights(min_samples=20):
    """Re-weight scoring signals from outcome history.

    For each signal, compute its correlation with correctness.  Signals
    that predict wins get stronger weights.  Signals that predict losses
    get weaker or inverted.  This is a simple gradient-following tuner --
    it gets smarter every day without needing a GPU or a data science team.
    """
    rows = _load_history()
    verdicts = [r for r in rows if "features" in r]
    outcomes = [r for r in rows if "features" not in r]

    if len(verdicts) < min_samples:
        return None, len(verdicts)

    # Match verdicts to outcomes by pair + approximate time
    scored = []
    for v in verdicts:
        for o in outcomes:
            if o["pair"] != v["pair"]:
                continue
            # Match by time proximity (same day)
            try:
                vt = datetime.fromisoformat(v["ts"])
                ot = datetime.fromisoformat(o["ts"])
                if abs((ot - vt).total_seconds()) < 36 * 3600:
                    scored.append({**v, "outcome": o["result"]})
                    break
            except Exception:
                continue

    if len(scored) < min_samples:
        return None, len(scored)

    # For each weight key, compute average outcome when signal was active
    new_weights = dict(WEIGHTS)
    keys = list(WEIGHTS.keys())
    signal_hits = {k: {"correct": 0, "wrong": 0, "missed": 0} for k in keys}

    for s in scored:
        result = s["outcome"]
        feats = s.get("features", {})
        w = s.get("weights", {})
        for k in keys:
            val = w.get(k, 0)
            if val == 0:
                continue
            bucket = signal_hits[k]
            if result == "CORRECT":
                bucket["correct"] += 1
            elif result == "WRONG":
                bucket["wrong"] += 1
            else:
                bucket["missed"] += 1

    for k, bucket in signal_hits.items():
        total = bucket["correct"] + bucket["wrong"] + bucket["missed"]
        if total < 5:
            continue
        # Correct rate when this signal fired
        rate = bucket["correct"] / total
        default = WEIGHTS[k]
        if rate > 0.6:
            # Signal works -- amplify
            new_weights[k] = round(default * 1.2, 2)
        elif rate < 0.4:
            # Signal hurts -- dampen toward zero
            new_weights[k] = round(default * 0.7, 2)
        else:
            new_weights[k] = default

    save_weights(new_weights)
    return new_weights, len(scored)

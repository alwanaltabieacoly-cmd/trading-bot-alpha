"""Alpha's own daily calls on Gate perps, scored by the same judge as the rules analyst, so the two can be compared fairly.
The caller supplies only coin, direction, stop%, target% and a reason. Everything that could leak the future is set here: entry is Gate's mark
price now, the time is now, the day key is the same one the rules analyst uses, one call per coin per day, and the file is append-only.
Calls are SCORED, not traded, until the auto-gate in gate_bot says otherwise.   Used by alpha/gate.py (MCP tool gate_alpha_call)."""
import json, time
from pathlib import Path
import gate_analyst as A

FILE = A.PRIVATE / "alpha_calls.jsonl"
TAGS = {"above_sma200", "below_sma200", "above_sma50", "below_sma50", "below_sma20", "rsi_oversold", "rsi_overbought", "funding_hot", "funding_neg",
        "news", "orderbook", "liquidations", "oi", "momentum", "mean_reversion", "breakout", "other"}   # free-form reasons go in `why`; tags let the judge group them

def day_key(now): return int(now) // 86400 * 86400 - 86400    # start of the last CLOSED daily bar, same as gate_analyst's `day`

def make_call(coin, call, stop_pct, target_pct, why, tags=(), path=None, now=None, mark=None, liquid=None):
    path, now = Path(path or FILE), int(now or time.time())
    if call not in ("long", "short", "flat"): raise ValueError("call must be long, short or flat")
    if not (why or "").strip(): raise ValueError("why is required: say what you saw")
    bad = [t for t in tags if t not in TAGS]
    if bad: raise ValueError(f"unknown tags {bad}; allowed: {sorted(TAGS)}")
    liquid = liquid if liquid is not None else {t["contract"] for t in A.liquid_contracts()}
    if coin not in liquid: raise ValueError(f"{coin} is not a liquid contract (>= ${A.MIN_VOL/1e6:.0f}M/day); try one of {sorted(liquid)[:8]}")
    if call != "flat":
        if not 0 < stop_pct <= 10: raise ValueError("stop_pct must be in (0, 10]: a stop is mandatory")
        if not 0 < target_pct <= 30: raise ValueError("target_pct must be in (0, 30]")
    day = day_key(now)
    if any(r["coin"] == coin and r["day"] == day for r in _rows(path)): raise ValueError(f"{coin} already called for this day; calls cannot be changed")
    rec = {"ts": now, "day": day, "coin": coin, "call": call, "horizon_h": A.HORIZON_H,
           "entry": float(mark if mark is not None else A.get(f"/futures/usdt/contracts/{coin}")["mark_price"]),
           "stop_pct": float(stop_pct) if call != "flat" else 0.0, "target_pct": float(target_pct) if call != "flat" else 0.0,
           "tags": ["alpha", *tags], "why": why.strip()[:600], "source": "alpha"}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f: f.write(json.dumps(rec) + "\n")
    return rec

def _rows(path): return [json.loads(x) for x in open(path) if x.strip()] if Path(path).exists() else []

"""Daily Gate analyst: one structured call per liquid USDT perp, from public data only.
call = {ts, coin, call: long|short|flat, horizon_h, entry, stop_pct, target_pct, tags[], ...}. Tags come from a fixed list so the judge can score each reason.
Rules use only bars closed at the call time. Run: python research/gate_analyst.py   -> appends to research/private/calls.jsonl"""
import json, sys, time, urllib.request
from pathlib import Path

HORIZON_H, MIN_VOL, SKIP = 24, 20e6, ("XAU", "XAG", "MU_", "INTC", "XAUT")
PRIVATE = Path(__file__).parent / "private"

def get(u):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + u, headers={"User-Agent": "alpha"}), timeout=20))
        except Exception: time.sleep(1)
    raise RuntimeError("Gate request failed: " + u)

def sma(x, n): return sum(x[-n:]) / n
def rsi(c, n=14):
    d = [c[i] - c[i-1] for i in range(1, len(c))]; ag = sum(max(x, 0) for x in d[:n]) / n; al = sum(max(-x, 0) for x in d[:n]) / n
    for x in d[n:]: ag, al = (ag*(n-1) + max(x, 0)) / n, (al*(n-1) + max(-x, 0)) / n
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
def atr_pct(h, l, c, n=14):
    tr = [max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])) for i in range(1, len(c))]; return sum(tr[-n:]) / n / c[-1] * 100

def decide(c, h, l, funding=0.0):
    """c,h,l = closed daily bars, oldest first, >= 201. Returns (call, tags, stop_pct, target_pct)."""
    px, s20, s50, s200, r, a = c[-1], sma(c, 20), sma(c, 50), sma(c, 200), rsi(c), atr_pct(h, l, c)
    tags = [t for t, ok in (("above_sma200", px > s200), ("below_sma200", px < s200), ("above_sma50", px > s50), ("below_sma50", px < s50),
                            ("below_sma20", px < s20), ("rsi_oversold", r < 40), ("rsi_overbought", r > 70), ("funding_hot", funding > 0.03), ("funding_neg", funding < -0.03)) if ok]
    stop, target = round(max(1.0, min(10.0, 0.6 * a)), 2), round(max(2.0, min(20.0, 1.2 * a)), 2)
    if px > s200 and px < s20 and r < 40: return "long", tags + ["setup_pullback"], stop, target
    if px > s50 > s200 and 50 <= r <= 70: return "long", tags + ["setup_trend"], stop, target
    if px < s200 and px < s50 and r > 40: return "short", tags + ["setup_breakdown"], stop, target
    return "flat", tags, stop, target

def liquid_contracts():
    tk = [t for t in get("/futures/usdt/tickers") if float(t["volume_24h_quote"]) >= MIN_VOL and not t["contract"].startswith(SKIP)]
    return sorted(tk, key=lambda t: -float(t["volume_24h_quote"]))

if __name__ == "__main__":
    PRIVATE.mkdir(exist_ok=True); now = int(time.time()); out = []
    for t in liquid_contracts():
        d = get(f"/futures/usdt/candlesticks?contract={t['contract']}&interval=1d&limit=260"); time.sleep(0.12)
        d = [x for x in d if x["t"] + 86400 <= now]  # closed bars only
        if len(d) < 201: continue
        c, h, l = [float(x["c"]) for x in d], [float(x["h"]) for x in d], [float(x["l"]) for x in d]
        call, tags, stop, target = decide(c, h, l, float(t["funding_rate"]) * 100)
        out.append({"ts": now, "day": d[-1]["t"], "coin": t["contract"], "call": call, "horizon_h": HORIZON_H, "entry": float(t["mark_price"]), "stop_pct": stop, "target_pct": target, "tags": tags})
    with open(PRIVATE / "calls.jsonl", "a") as f:
        for o in out: f.write(json.dumps(o) + "\n")
    n = {k: sum(o["call"] == k for o in out) for k in ("long", "short", "flat")}
    print(f"{len(out)} coins: {n}")
    for o in out:
        if o["call"] != "flat": print(f"  {o['call']:5s} {o['coin']:10s} entry {o['entry']:<10g} stop {o['stop_pct']}% target {o['target_pct']}%  {','.join(o['tags'])}")

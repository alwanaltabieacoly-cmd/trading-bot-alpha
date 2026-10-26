"""Judge for gate_analyst calls. Resolves each call on Gate hourly candles (stop checked before target within a bar), subtracts cost,
and reports per-tag accuracy with a Wilson 95% lower bound, mean net return, and a same-direction hold baseline (no stop or target) over the same windows.
  python research/gate_judge.py live        score calls in private/calls.jsonl whose horizon has passed
  python research/gate_judge.py backfill    replay the analyst rules over ~400 days of hourly history (in-sample sanity check, not proof)"""
import json, math, sys, time
from collections import defaultdict
from pathlib import Path
import gate_analyst as A

COST = 0.10  # percent, round trip at the account's futures taker rate (0.05% x 2). Market entry; stop is a market close.

def resolve(side, entry, stop_pct, target_pct, bars):
    """bars: [(high, low, close)] after entry. Returns (net_return_pct, outcome)."""
    sgn = 1 if side == "long" else -1
    for h, l, _ in bars:
        worst, best = ((l, h) if sgn == 1 else (h, l))
        if sgn * (worst / entry - 1) * 100 <= -stop_pct: return -stop_pct - COST, "stop"
        if sgn * (best / entry - 1) * 100 >= target_pct: return target_pct - COST, "target"
    return sgn * (bars[-1][2] / entry - 1) * 100 - COST, "timeout"

def wilson_lower(w, n, z=1.96):
    if n == 0: return 0.0
    p = w / n; return (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1 + z*z/n)

def hourly(contract, start, end):
    out, to = [], end
    while to > start:
        r = A.get(f"/futures/usdt/candlesticks?contract={contract}&interval=1h&from={max(start, to-1999*3600)}&to={to}"); time.sleep(0.12)
        if not r: break
        out = r + out; to = r[0]["t"] - 3600
    return {x["t"]: (float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"])) for x in out}

def report(rows, title):
    """rows: dicts with tags, net, base (always-long net over the same window), coin, day."""
    lines = [f"## {title}", "", "| Tag | n | win% | 95% lower | mean net % | same-direction hold % |", "|---|---|---|---|---|---|"]
    groups = defaultdict(list)
    for r in rows:
        for t in r["tags"] + ["ALL"]: groups[t].append(r)
    for t, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        w = sum(r["net"] > 0 for r in rs); n = len(rs)
        lines.append(f"| {t} | {n} | {w/n:.0%} | {wilson_lower(w, n):.0%} | {sum(r['net'] for r in rs)/n:+.3f} | {sum(r['base'] for r in rs)/n:+.3f} |")
    return "\n".join(lines)

def backfill(coins, days=400):
    now = int(time.time()); rows = []
    for t in coins:
        c = t["contract"]; d = A.get(f"/futures/usdt/candlesticks?contract={c}&interval=1d&limit=1000"); time.sleep(0.12)
        if len(d) < 260: continue
        hb = hourly(c, max(d[200]["t"], now - 9900*3600), now)  # Gate serves only the latest 10,000 hourly bars
        cl, hi, lo = [float(x["c"]) for x in d], [float(x["h"]) for x in d], [float(x["l"]) for x in d]
        for i in range(200, len(d) - 2):
            side, tags, stop, target = A.decide(cl[:i+1], hi[:i+1], lo[:i+1])
            if side == "flat": continue
            t0 = d[i]["t"] + 86400  # next UTC midnight: first hour after the signal bar closed
            window = [hb[t0 + 3600*k] for k in range(A.HORIZON_H) if t0 + 3600*k in hb]
            if len(window) < A.HORIZON_H: continue
            entry = window[0][0]; bars = [(w[1], w[2], w[3]) for w in window]
            net, out = resolve(side, entry, stop, target, bars)
            base = (bars[-1][2] / entry - 1) * 100 * (1 if side == "long" else -1) - COST  # same direction, no stop/target
            rows.append({"coin": c, "day": t0, "side": side, "tags": tags, "net": net, "base": base, "out": out})
    return rows

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "live"
    if mode == "backfill":
        rows = backfill(A.liquid_contracts()[:int(sys.argv[2]) if len(sys.argv) > 2 else 15])
        # one count per coin per day already; split in time halves
        rows.sort(key=lambda r: r["day"]); half = len(rows) // 2
        (A.PRIVATE / "backfill_rows.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        txt = [f"# Backfill of analyst rules ({len(rows)} calls, {len({r['coin'] for r in rows})} coins, in-sample, cost {COST}% round trip)", "",
               "Calls overlap across coins on the same day (crypto is highly correlated), so effective n is much smaller than shown.", "",
               report(rows, "All"), "", report(rows[:half], "First half"), "", report(rows[half:], "Second half")]
        (A.PRIVATE / "BACKFILL.md").write_text("\n".join(txt), encoding="utf-8"); print("\n".join(txt))
    else:
        calls = [json.loads(x) for x in open(A.PRIVATE / "calls.jsonl")] if (A.PRIVATE / "calls.jsonl").exists() else []
        done = {(r["coin"], r["day"]) for r in map(json.loads, open(A.PRIVATE / "scored.jsonl"))} if (A.PRIVATE / "scored.jsonl").exists() else set()
        now, new = time.time(), []
        for c in calls:
            if c["call"] == "flat" or (c["coin"], c["day"]) in done or c["ts"] + c["horizon_h"]*3600 > now: continue
            hb = hourly(c["coin"], c["ts"] - 3600, int(c["ts"] + c["horizon_h"]*3600)); ks = sorted(k for k in hb if k >= c["ts"] - 3600)[:c["horizon_h"]]
            if len(ks) < c["horizon_h"]: continue
            bars = [(hb[k][1], hb[k][2], hb[k][3]) for k in ks]; net, out = resolve(c["call"], c["entry"], c["stop_pct"], c["target_pct"], bars)
            base = (bars[-1][2] / c["entry"] - 1) * 100 * (1 if c["call"] == "long" else -1) - COST
            new.append({**c, "net": net, "base": base, "out": out})
        with open(A.PRIVATE / "scored.jsonl", "a") as f:
            for r in new: f.write(json.dumps(r) + "\n")
        print(f"scored {len(new)} new calls; {len(calls)-len(new)} waiting/flat/already scored")

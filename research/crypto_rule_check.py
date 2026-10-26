"""SMA200-only long/flat rule per coin, split into halves, 0.10%/side. Compare with buy&hold and with the ATR<4% version."""
import json, time, urllib.request
FEE = 0.001
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + u, headers={"User-Agent": "alpha"}), timeout=20))
def run(c, h, l, lo, hi, atr_cap):
    eq = bh = 1.0; pos = 0; inn = tr = 0; peak = 1.0; mdd = 0.0
    for i in range(lo, hi):
        s = sum(c[i-199:i+1]) / 200
        a = sum(max(h[j]-l[j], abs(h[j]-c[j-1]), abs(l[j]-c[j-1])) for j in range(i-29, i+1)) / 30 / c[i]
        want = 1 if c[i] > s and (atr_cap is None or a < atr_cap) else 0
        if want != pos: eq *= 1 - FEE; pos = want; tr += 1
        r = c[i+1]/c[i] - 1
        if pos: eq *= 1 + r; inn += 1
        bh *= 1 + r; peak = max(peak, eq); mdd = max(mdd, 1 - eq/peak)
    return eq - 1, bh - 1, inn / (hi - lo), tr, mdd
tk = sorted([t for t in get("/futures/usdt/tickers") if float(t["volume_24h_quote"]) >= 20e6], key=lambda t: -float(t["volume_24h_quote"]))
names = [t["contract"] for t in tk if not t["contract"].startswith(("XAU", "XAG", "MU_", "INTC"))]
res = []
for n in names:
    d = get(f"/futures/usdt/candlesticks?contract={n}&interval=1d&limit=1000"); time.sleep(0.12)
    if len(d) < 520: continue
    c, h, l = [float(x["c"]) for x in d], [float(x["h"]) for x in d], [float(x["l"]) for x in d]
    m = 200 + (len(c) - 201) // 2
    row = {"coin": n[:-5], "days": len(c) - 201}
    for tag, cap in (("sma", None), ("sma+atr", 0.04)):
        row[tag] = [run(c, h, l, 200, m, cap), run(c, h, l, m, len(c) - 1, cap)]
    res.append(row)
print(f"{'coin':6s} {'days':>4s} | SMA200 only: H1 rule/BH   H2 rule/BH   inMkt  trades | SMA+ATR: H1   H2")
w1 = w2 = 0
for r in res:
    (a1, b1, i1, t1, _), (a2, b2, i2, t2, _) = r["sma"]; (c1, *_), (c2, *_) = r["sma+atr"]
    w1 += a1 > 0; w2 += a2 > 0
    print(f"{r['coin']:6s} {r['days']:4d} | {a1:+8.0%}/{b1:+6.0%}  {a2:+8.0%}/{b2:+6.0%}  {i2:4.0%}  {t1+t2:3d} | {c1:+5.0%} {c2:+5.0%}")
print(f"\ncoins {len(res)}: SMA200-only positive in H1 {w1}, in H2 {w2}; beat buy&hold H2 {sum(r['sma'][1][0] > r['sma'][1][1] for r in res)}; lower maxDD H2 {sum(r['sma'][1][4] < 1 for r in res)}")

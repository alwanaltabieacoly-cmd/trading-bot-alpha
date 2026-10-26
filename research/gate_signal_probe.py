"""Test candle-based 1m signals on Gate USDT-perp history. Non-overlapping events, costs from account fees.
Run: python research/gate_signal_probe.py [BTC_USDT ETH_USDT ...]"""
import json, math, sys, time, urllib.request

def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + url, headers={"User-Agent": "alpha"}), timeout=20))

def candles(contract, pages=5):
    out, to = [], int(time.time())
    for _ in range(pages):
        if to < time.time() - 9900 * 60: break
        r = get(f"/futures/usdt/candlesticks?contract={contract}&interval=1m&from={to-119940}&to={to}")
        if not r: break
        out = r + out; to = r[0]["t"] - 60  # Gate keeps only the latest 10,000 1m bars; time.sleep(0.15)
    return [(c["t"], float(c["o"]), float(c["h"]), float(c["l"]), float(c["c"]), float(c["v"])) for c in out]

SIGNALS = {  # return +1 long, -1 short, 0 none; uses only bars up to i
    "sweep_low_reversal":  lambda b, i: 1 if b[i][3] < min(x[3] for x in b[i-30:i]) and b[i][4] > b[i][1] else 0,
    "sweep_high_reversal": lambda b, i: -1 if b[i][2] > max(x[2] for x in b[i-30:i]) and b[i][4] < b[i][1] else 0,
    "volspike_continue":   lambda b, i: (1 if b[i][4] > b[i][1] else -1) if b[i][5] > 3 * sum(x[5] for x in b[i-30:i]) / 30 else 0,
    "volspike_fade":       lambda b, i: (-1 if b[i][4] > b[i][1] else 1) if b[i][5] > 3 * sum(x[5] for x in b[i-30:i]) / 30 else 0,
    "momentum_5":          lambda b, i: 1 if b[i][4] / b[i-5][4] > 1.002 else (-1 if b[i][4] / b[i-5][4] < 0.998 else 0),
}
TP = SL = 0.003; H = 30; TAKER_RT, MAKER_RT = 0.0010, 0.0004

def trade(b, i, d):
    e = b[i][4]
    for j in range(i + 1, min(i + 1 + H, len(b))):
        lo, hi = (b[j][3], b[j][2]) if d == 1 else (-b[j][2], -b[j][3])
        worst, best = (lo / e - 1) if d == 1 else (1 - b[j][2] / e), (hi / e - 1) if d == 1 else (1 - b[j][3] / e)
        if worst <= -SL: return -SL
        if best >= TP: return TP
    j = min(i + H, len(b) - 1); return d * (b[j][4] / e - 1)

for c in (sys.argv[1:] or ["BTC_USDT", "ETH_USDT", "SOL_USDT"]):
    b = candles(c); half = len(b) // 2
    print(f"\n{c}: {len(b)} bars ({(b[-1][0]-b[0][0])/86400:.1f} days). first half / second half shown separately")
    for name, f in SIGNALS.items():
        row = []
        for lo, hi in ((31, half), (half, len(b) - H - 1)):
            rets, i = [], lo
            while i < hi:
                d = f(b, i)
                if d: rets.append(trade(b, i, d)); i += H   # non-overlapping
                else: i += 1
            n = len(rets); m = sum(rets) / n if n else 0
            sd = math.sqrt(sum((r - m) ** 2 for r in rets) / (n - 1)) if n > 2 else 0
            row.append((n, m, m / (sd / math.sqrt(n)) if sd else 0, sum(r > 0 for r in rets) / n if n else 0))
        print(f"{name:20s} " + " | ".join(f"n={n:4d} gross {m:+.4%} t={t:+.1f} win {w:.0%} net(maker) {m-MAKER_RT:+.3%}" for n, m, t, w in row))

"""Gate public-data collector: runs on GitHub Actions (PC off) or locally. No API key.
Every 10 s: order-book top-10 per coin (mid, spread, imbalance). Same tick: trade tape and liquidations (Gate keeps only ~2 minutes of
tape, so it must be recorded as it happens). One CSV row per coin per complete minute -> research/gate_data/YYYY-MM-DD.csv.
  python research/gate_collect.py 55       collect for 55 minutes
  python research/gate_collect.py coverage show rows per day against the 1440 minutes a day should have
Columns: imb = (bid size - ask size)/(sum) over the top 10 levels; buy_vol/sell_vol = taker contracts (Gate sign: size>0 buyer-taker);
liq_size = signed sum of liquidated contracts as Gate returns it."""
import csv, os, sys, time, urllib.request, json
from collections import defaultdict
from pathlib import Path
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "LINK", "LTC"]
OUT = Path(os.environ.get("ALPHA_DATA_DIR") or Path(__file__).parent / "gate_data")
FIELDS = ["minute", "coin", "mid", "spread_bps", "imb", "buy_vol", "sell_vol", "trades", "liq_n", "liq_size", "samples"]

def get(u):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + u, headers={"User-Agent": "alpha"}), timeout=15))
        except Exception: time.sleep(0.5)
    return None

def book_stats(b):
    p = lambda x: float(x["p"] if isinstance(x, dict) else x[0]); s = lambda x: abs(float(x["s"] if isinstance(x, dict) else x[1]))
    bid, ask = p(b["bids"][0]), p(b["asks"][0]); mid = (bid + ask) / 2
    bv, av = sum(map(s, b["bids"][:10])), sum(map(s, b["asks"][:10]))
    return mid, (ask - bid) / mid * 1e4, (bv - av) / (bv + av) if bv + av else 0.0

def write(rows):
    OUT.mkdir(parents=True, exist_ok=True)
    for r in rows:
        f = OUT / (time.strftime("%Y-%m-%d", time.gmtime(r["minute"] * 60)) + ".csv"); new = not f.exists()
        with open(f, "a", newline="") as h:
            w = csv.DictWriter(h, FIELDS); new and w.writeheader(); w.writerow(r)

def collect(minutes):
    start = time.time(); end = start + minutes * 60; first = int(start // 60) + 1   # the minute we started in is partial: skip it
    acc = defaultdict(lambda: {"mid": 0.0, "sp": [], "imb": [], "buy": 0.0, "sell": 0.0, "n": 0, "liq_n": 0, "liq": 0.0})
    last_trade, last_liq, done = {}, {}, set()
    def flush(upto):
        rows = []
        for (c, m), a in sorted(acc.items(), key=lambda kv: kv[0][1]):
            if m < upto and (c, m) not in done and a["sp"]:
                done.add((c, m)); rows.append({"minute": m, "coin": c, "mid": a["mid"], "spread_bps": round(sum(a["sp"]) / len(a["sp"]), 3),
                    "imb": round(sum(a["imb"]) / len(a["imb"]), 4), "buy_vol": a["buy"], "sell_vol": a["sell"], "trades": a["n"],
                    "liq_n": a["liq_n"], "liq_size": a["liq"], "samples": len(a["sp"])})
        write(rows); return len(rows)
    total = 0
    while time.time() < end:
        t0 = time.time(); m = int(t0 // 60)
        for c in COINS:
            try:
                b = get(f"/futures/usdt/order_book?contract={c}_USDT&limit=10")
                mid, sp, imb = book_stats(b); a = acc[(c, m)]; a["mid"] = mid; a["sp"].append(sp); a["imb"].append(imb)
            except Exception: pass
            for t in reversed(get(f"/futures/usdt/trades?contract={c}_USDT&limit=1000") or []):
                if t["id"] <= last_trade.get(c, 0): continue
                last_trade[c] = t["id"]; a = acc[(c, int(t["create_time"] // 60))]; a["n"] += 1; a["buy" if t["size"] > 0 else "sell"] += abs(t["size"])
            for l in get(f"/futures/usdt/liq_orders?contract={c}_USDT&limit=100") or []:
                if l["time"] <= last_liq.get(c, 0): continue
                last_liq[c] = max(last_liq.get(c, 0), l["time"]); a = acc[(c, l["time"] // 60)]; a["liq_n"] += 1; a["liq"] += float(l["size"])
        total += flush(int(time.time() // 60) - 1)
        time.sleep(max(0, 10 - (time.time() - t0)))
    total += flush(int(time.time() // 60))   # every minute that finished before we stopped
    print(f"wrote {total} coin-minutes ({minutes} min run, minutes before #{first} skipped as partial)")

def coverage():
    for f in sorted(OUT.glob("*.csv")):
        n = sum(1 for _ in open(f)) - 1; mins = len({l.split(",")[0] for l in list(open(f))[1:]})
        print(f"{f.stem}: {n} rows, {mins} distinct minutes of 1440 ({mins/1440:.0%})")

if __name__ == "__main__":
    coverage() if sys.argv[1:2] == ["coverage"] else collect(float(sys.argv[1]) if len(sys.argv) > 1 else 5)

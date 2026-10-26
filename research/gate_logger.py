"""Log Gate.io public market data for microstructure research (no API key needed).
Every INTERVAL s: top-20 order book snapshot per pair. Every minute: closed 1m candle.
Output: research/data/gate/<PAIR>_book.jsonl and <PAIR>_1m.jsonl (append-only, resumable).
Run:  python research/gate_logger.py [seconds_between_book_snapshots]
"""
import json, sys, time, urllib.request
from pathlib import Path

PAIRS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT"]
OUT = Path(__file__).parent / "data" / "gate"
INTERVAL = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0

def get(path):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + path, headers={"User-Agent": "alpha"}), timeout=10))

def append(name, row):
    with open(OUT / name, "a") as f: f.write(json.dumps(row, separators=(",", ":")) + "\n")

def last_candle_ts(pair):
    p = OUT / f"{pair}_1m.jsonl"
    if not p.exists() or p.stat().st_size == 0: return 0
    return json.loads(p.read_text().strip().splitlines()[-1])["t"]

OUT.mkdir(parents=True, exist_ok=True)
seen = {p: last_candle_ts(p) for p in PAIRS}
while True:
    t0 = time.time()
    for p in PAIRS:
        try:
            b = get(f"/spot/order_book?currency_pair={p}&limit=20")
            append(f"{p}_book.jsonl", {"t": round(t0, 2), "bids": b["bids"], "asks": b["asks"]})
            for c in get(f"/spot/candlesticks?currency_pair={p}&interval=1m&limit=3"):
                ts = int(c[0])
                if c[7] == "true" and ts > seen[p]:  # closed candles only
                    append(f"{p}_1m.jsonl", {"t": ts, "vol_quote": float(c[1]), "c": float(c[2]), "h": float(c[3]), "l": float(c[4]), "o": float(c[5]), "vol": float(c[6])})
                    seen[p] = ts
        except Exception as e:
            print(time.strftime("%H:%M:%S"), p, "error:", e, flush=True); time.sleep(5)
    time.sleep(max(0, INTERVAL - (time.time() - t0)))

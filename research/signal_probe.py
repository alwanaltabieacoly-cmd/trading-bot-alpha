"""Signal probe: compute indicator predictive power (IC/IR) across assets."""
import json, math, sys, os
from datetime import datetime, timezone

PAIRS = ["BTC-USDT","ETH-USDT","SOL-USDT","BNB-USDT","XRP-USDT","ADA-USDT","DOGE-USDT"]

def rsi(closes, period=14):
    if len(closes) < period + 1: return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d,0)); losses.append(max(-d,0))
    avg_g = sum(gains[-period:])/period
    avg_l = sum(losses[-period:])/period
    if avg_l == 0: return 100.0
    return 100.0 - 100.0/(1.0 + avg_g/avg_l)

def macd_hist(closes, fast=12, slow=26, signal=9):
    if len(closes) < slow + signal: return None
    def ema(vals, n):
        k = 2/(n+1); e = vals[0]
        for v in vals[1:]: e = v*k + e*(1-k)
        return e
    ema_fast = ema(closes, fast); ema_slow = ema(closes, slow)
    macd = ema_fast - ema_slow
    # signal line from macd series
    macd_series = []
    for i in range(len(closes)):
        f = ema(closes[:i+1], fast) if i >= fast else closes[i]
        s = ema(closes[:i+1], slow) if i >= slow else closes[i]
        macd_series.append(f - s)
    sig = ema(macd_series, signal) if len(macd_series) >= signal else macd_series[-1]
    return macd - sig

def boll_width(closes, n=20, k=2.0):
    if len(closes) < n: return None
    window = closes[-n:]
    mean = sum(window)/n
    std = math.sqrt(sum((x-mean)**2 for x in window)/n)
    return (mean + k*std - (mean - k*std)) / mean if mean else None

def sma_dist(closes, n=20):
    if len(closes) < n: return None
    mean = sum(closes[-n:])/n
    return (closes[-1] - mean)/mean if mean else None

def vol_ratio(closes, vols, n=20):
    if len(vols) < n: return None
    return vols[-1] / (sum(vols[-n:])/n) if sum(vols[-n:]) else None

def fwd_ret(closes, horizon=1):
    if len(closes) < horizon + 1: return None
    return closes[-1] / closes[-horizon-1] - 1.0

def load_hourly():
    data = json.load(open("D:/AlphaCode/bot-repo/research/market_cache_hourly.json"))
    return data

def main():
    data = load_hourly()
    rows = []
    for pair in PAIRS:
        bars = data.get(pair, [])
        if len(bars) < 50: continue
        closes = [b["close"] for b in bars]
        vols = [b["volume"] for b in bars]
        for i in range(48, len(closes)-2):
            c = closes[:i+1]; v = vols[:i+1]
            r = rsi(c)
            mh = macd_hist(c)
            bw = boll_width(c)
            sd = sma_dist(c)
            vr = vol_ratio(c, v)
            fr = fwd_ret(closes, 1)
            fr3 = fwd_ret(closes, 3)
            if r is None or fr is None: continue
            rows.append({"pair": pair, "idx": i, "close": closes[i], "rsi": r,
                         "macd_hist": mh, "boll_width": bw, "sma_dist": sd,
                         "vol_ratio": vr, "fwd_1h": fr, "fwd_3h": fr3})
    json.dump(rows, open("D:/AlphaCode/bot-repo/research/signal_rows.json","w"), indent=1)
    print(f"signal rows: {len(rows)}")

    # IC = Spearman rank correlation between indicator and forward return
    for ind in ("rsi","macd_hist","boll_width","sma_dist","vol_ratio"):
        vals = [(r[ind], r["fwd_1h"]) for r in rows if r[ind] is not None]
        if len(vals) < 20: continue
        n = len(vals)
        # rank
        xs = sorted(vals, key=lambda x: x[0]); ys = sorted(vals, key=lambda x: x[1])
        rank_x = {v: i for i, v in enumerate(xs)}
        rank_y = {v: i for i, v in enumerate(ys)}
        d2 = sum((rank_x[(a,b)] - rank_y[(a,b)])**2 for a,b in vals)
        ic = 1 - 6*d2/(n*(n*n-1))
        # IR = IC / std
        # per-pair IC
        pair_ics = {}
        for p in PAIRS:
            pv = [(r[ind], r["fwd_1h"]) for r in rows if r[ind] is not None and r["pair"]==p]
            if len(pv) < 10: continue
            m = len(pv)
            px = sorted(pv, key=lambda x: x[0]); py = sorted(pv, key=lambda x: x[1])
            rx = {v:i for i,v in enumerate(px)}; ry = {v:i for i,v in enumerate(py)}
            dd2 = sum((rx[(a,b)]-ry[(a,b)])**2 for a,b in pv)
            pair_ics[p] = round(1 - 6*dd2/(m*(m*m-1)), 4)
        print(f"{ind:12s} IC={ic:+.4f}  n={n:5d}  per-pair: {pair_ics}")

if __name__ == "__main__":
    main()
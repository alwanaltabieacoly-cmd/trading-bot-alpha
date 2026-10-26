"""Full-market crypto scan on Gate USDT perps (public data). Writes research/CRYPTO_SCAN.md.
Per coin: trend (SMA20/50/200), RSI14, ATR%, returns, relative strength vs BTC, liquidity, funding,
plus a daily backtest of the rule  hold = close > SMA200 and ATR30/close < 4%  vs buy&hold (0.10% per side)."""
import json, math, time, urllib.request, datetime as dt
MIN_VOL, TOP, FEE = 5e6, 60, 0.001

def get(u):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + u, headers={"User-Agent": "alpha"}), timeout=20))
        except Exception: time.sleep(1)
    return None

def sma(x, n): return sum(x[-n:]) / n
def rsi(c, n=14):
    g = [max(c[i]-c[i-1], 0) for i in range(1, len(c))]; l = [max(c[i-1]-c[i], 0) for i in range(1, len(c))]
    ag, al = sum(g[:n])/n, sum(l[:n])/n
    for i in range(n, len(g)): ag, al = (ag*(n-1)+g[i])/n, (al*(n-1)+l[i])/n
    return 100 if al == 0 else 100 - 100/(1+ag/al)
def atr_pct(h, l, c, n=30):
    tr = [max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])) for i in range(1, len(c))]
    return sum(tr[-n:]) / n / c[-1]

def backtest(c, h, l):
    eq = bh = 1.0; peak = bpeak = 1.0; mdd = bmdd = 0.0; pos = 0; days_in = 0; trades = 0
    for i in range(200, len(c) - 1):
        want = 1 if c[i] > sma(c[:i+1], 200) and atr_pct(h[:i+1], l[:i+1], c[:i+1]) < 0.04 else 0
        if want != pos: eq *= 1 - FEE; pos = want; trades += 1
        r = c[i+1] / c[i] - 1
        if pos: eq *= 1 + r; days_in += 1
        bh *= 1 + r
        peak, bpeak = max(peak, eq), max(bpeak, bh); mdd, bmdd = max(mdd, 1-eq/peak), max(bmdd, 1-bh/bpeak)
    n = len(c) - 201
    return dict(days=n, strat=eq-1, bh=bh-1, mdd=mdd, bh_mdd=bmdd, in_mkt=days_in/n, trades=trades)

tk = [t for t in get("/futures/usdt/tickers") if float(t["volume_24h_quote"]) >= MIN_VOL]
tk.sort(key=lambda t: -float(t["volume_24h_quote"])); tk = tk[:TOP]
print(len(tk), "contracts above $%.0fM 24h volume" % (MIN_VOL/1e6))
rows, btc30 = [], None
for t in tk:
    name = t["contract"]; d = get(f"/futures/usdt/candlesticks?contract={name}&interval=1d&limit=1000"); time.sleep(0.12)
    if not d or len(d) < 260: continue
    c, h, l = [float(x["c"]) for x in d], [float(x["h"]) for x in d], [float(x["l"]) for x in d]
    bid, ask = float(t.get("highest_bid") or 0), float(t.get("lowest_ask") or 0)
    r = dict(name=name.replace("_USDT", ""), px=c[-1], vol=float(t["volume_24h_quote"]), spread_bps=(ask-bid)/((ask+bid)/2)*1e4 if bid and ask else 99,
             funding=float(t["funding_rate"])*100, d1=c[-1]/c[-2]-1, d7=c[-1]/c[-8]-1, d30=c[-1]/c[-31]-1, d90=c[-1]/c[-91]-1,
             s20=c[-1]/sma(c,20)-1, s50=c[-1]/sma(c,50)-1, s200=c[-1]/sma(c,200)-1, rsi=rsi(c), atr=atr_pct(h,l,c),
             off_hi=c[-1]/max(c[-90:])-1, off_lo=c[-1]/min(c[-90:])-1, hist=len(c), bt=backtest(c, h, l))
    r["on"] = r["s200"] > 0 and r["atr"] < 0.04
    rows.append(r)
    if r["name"] == "BTC": btc30 = r["d30"]
for r in rows: r["rs30"] = r["d30"] - btc30
json.dump(rows, open("data/crypto_scan.json", "w"))

now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
pc = lambda x: f"{x:+.1%}"
out = [f"# Crypto Full-Market Scan — {now}", "", f"Universe: top {len(rows)} Gate USDT perps by 24h volume (>= ${MIN_VOL/1e6:.0f}M). Source: Gate public API. Daily bars, up to 1000 per coin.", ""]
bt_ok = [r for r in rows if r["bt"]["days"] >= 300]
beat = [r for r in bt_ok if r["bt"]["strat"] > r["bt"]["bh"]]
ddbetter = [r for r in bt_ok if r["bt"]["mdd"] < r["bt"]["bh_mdd"]]
pos = [r for r in bt_ok if r["bt"]["strat"] > 0]
med = lambda xs: sorted(xs)[len(xs)//2]
out += ["## 1. Market breadth", f"- Above SMA200: {sum(r['s200']>0 for r in rows)}/{len(rows)} | above SMA50: {sum(r['s50']>0 for r in rows)}/{len(rows)} | above SMA20: {sum(r['s20']>0 for r in rows)}/{len(rows)}",
        f"- Median 7d {pc(med([r['d7'] for r in rows]))}, 30d {pc(med([r['d30'] for r in rows]))}, 90d {pc(med([r['d90'] for r in rows]))}",
        f"- Median RSI14 {med([r['rsi'] for r in rows]):.0f}; median funding {med([r['funding'] for r in rows]):+.4f}%/8h",
        f"- SMA200+ATR rule currently ON for {sum(r['on'] for r in rows)}/{len(rows)} coins", ""]
out += ["## 2. Rule backtest on every coin (daily, long/flat, 0.10% per side, in-sample, survivors only)",
        f"- Coins tested: {len(bt_ok)}. Rule made money on {len(pos)}, beat buy&hold on {len(beat)}, had smaller max drawdown on {len(ddbetter)}.",
        f"- Median: rule {pc(med([r['bt']['strat'] for r in bt_ok]))} vs buy&hold {pc(med([r['bt']['bh'] for r in bt_ok]))}; max drawdown rule {med([r['bt']['mdd'] for r in bt_ok]):.0%} vs buy&hold {med([r['bt']['bh_mdd'] for r in bt_ok]):.0%}; time in market {med([r['bt']['in_mkt'] for r in bt_ok]):.0%}", "",
        "| Coin | Days | Rule | Buy&Hold | Rule maxDD | B&H maxDD | In mkt | Trades |", "|---|---|---|---|---|---|---|---|"]
for r in sorted(bt_ok, key=lambda r: -r["vol"])[:25]:
    b = r["bt"]; out.append(f"| {r['name']} | {b['days']} | {pc(b['strat'])} | {pc(b['bh'])} | {b['mdd']:.0%} | {b['bh_mdd']:.0%} | {b['in_mkt']:.0%} | {b['trades']} |")
out += ["", "## 3. Current state, all coins (sorted by 24h volume)", "| Coin | Price | 24h vol $M | Spread bps | 7d | 30d | vs BTC 30d | RSI | vs SMA50 | vs SMA200 | ATR% | Funding %/8h | Rule |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in sorted(rows, key=lambda r: -r["vol"]):
    out.append(f"| {r['name']} | {r['px']:.6g} | {r['vol']/1e6:.0f} | {r['spread_bps']:.1f} | {pc(r['d7'])} | {pc(r['d30'])} | {pc(r['rs30'])} | {r['rsi']:.0f} | {pc(r['s50'])} | {pc(r['s200'])} | {r['atr']:.1%} | {r['funding']:+.4f} | {'ON' if r['on'] else 'off'} |")
liq = [r for r in rows if r["vol"] >= 20e6 and r["spread_bps"] < 5]
out += ["", "## 4. Watchlists (liquid only: >= $20M volume, spread < 5 bps)",
        "**Rule ON (above SMA200, ATR<4%), strongest vs BTC:** " + (", ".join(f"{r['name']} ({pc(r['rs30'])})" for r in sorted([r for r in liq if r['on']], key=lambda r: -r['rs30'])[:10]) or "none"),
        "", "**Oversold (RSI<35) but above SMA200 — pullback in an uptrend:** " + (", ".join(f"{r['name']} (RSI {r['rsi']:.0f})" for r in sorted([r for r in liq if r['rsi']<35 and r['s200']>0], key=lambda r: r['rsi'])) or "none"),
        "", "**Overheated funding (> +0.03%/8h, crowded longs):** " + (", ".join(f"{r['name']} ({r['funding']:+.3f})" for r in sorted([r for r in rows if r['funding']>0.03], key=lambda r: -r['funding'])) or "none"),
        "", "**Negative funding (< -0.03%/8h, crowded shorts):** " + (", ".join(f"{r['name']} ({r['funding']:+.3f})" for r in sorted([r for r in rows if r['funding']<-0.03], key=lambda r: r['funding'])) or "none"),
        "", "**Strongest 30d vs BTC:** " + ", ".join(f"{r['name']} ({pc(r['rs30'])})" for r in sorted(liq, key=lambda r: -r['rs30'])[:8]),
        "", "**Weakest 30d vs BTC:** " + ", ".join(f"{r['name']} ({pc(r['rs30'])})" for r in sorted(liq, key=lambda r: r['rs30'])[:8])]
open("CRYPTO_SCAN.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[:22])); print("..."); print("\n".join(out[-12:]))

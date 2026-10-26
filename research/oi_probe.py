"""Do Gate's derivatives stats (open interest, long/short ratios, liquidations) predict the next day's return?
500 daily buckets per coin from /futures/usdt/contract_stats. Features at bucket t, return from t+1 to t+2 (one bucket skipped so a feature that
includes the end of its bucket cannot leak into the return). Rank correlation (IC) pooled over coins, split in time halves.
A feature counts only if the sign agrees in both halves and |IC| clears the noise level 2/sqrt(n)."""
import json, math, sys, time, urllib.request
import numpy as np, pandas as pd
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "LINK", "LTC", "AVAX", "ADA", "SUI", "NEAR"]
def get(u):
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + u, headers={"User-Agent": "alpha"}), timeout=25))
        except Exception: time.sleep(1)
    return []
rows = []
for c in COINS:
    d = get(f"/futures/usdt/contract_stats?contract={c}_USDT&interval=1d&limit=500"); time.sleep(0.15)
    if len(d) < 200: continue
    df = pd.DataFrame(d).sort_values("time").reset_index(drop=True)
    for k in ("open_interest", "mark_price", "lsr_taker", "lsr_account", "long_liq_usd", "short_liq_usd", "top_lsr_size"):
        df[k] = pd.to_numeric(df.get(k), errors="coerce")
    df["oi_chg"] = df["open_interest"].pct_change()
    df["px_chg"] = df["mark_price"].pct_change()
    df["liq_imb"] = (df["long_liq_usd"] - df["short_liq_usd"]) / (df["long_liq_usd"] + df["short_liq_usd"] + 1)
    df["lsr_acct_z"] = (df["lsr_account"] - df["lsr_account"].rolling(60).mean()) / df["lsr_account"].rolling(60).std()
    df["lsr_taker_z"] = (df["lsr_taker"] - df["lsr_taker"].rolling(60).mean()) / df["lsr_taker"].rolling(60).std()
    df["oi_up_px_up"] = np.sign(df["oi_chg"]) * np.sign(df["px_chg"])   # +1 new money agrees with price, -1 squeeze/cover
    df["fwd"] = df["mark_price"].shift(-2) / df["mark_price"].shift(-1) - 1
    df["coin"] = c; rows.append(df)
D = pd.concat(rows).dropna(subset=["fwd"]); print(f"{D.coin.nunique()} coins, {len(D)} coin-days, {D.time.min():.0f}..{D.time.max():.0f}")
D["rk_fwd"] = D.groupby("time")["fwd"].rank()   # cross-sectional: compare coins on the same day, removes the market-wide move
mid = D.time.median()
FEATS = ["oi_chg", "px_chg", "liq_imb", "lsr_acct_z", "lsr_taker_z", "oi_up_px_up", "top_lsr_size"]
print(f"\n{'feature':14s} {'IC all':>8s} {'first':>8s} {'second':>8s} {'noise':>7s}  verdict")
for f in FEATS:
    x = D.dropna(subset=[f]); ics = []
    for part in (x, x[x.time <= mid], x[x.time > mid]):
        ics.append(part[f].rank().corr(part["rk_fwd"]) if len(part) > 50 else float("nan"))
    noise = 2 / math.sqrt(len(x)); ok = all(abs(i) > noise for i in ics[1:]) and np.sign(ics[1]) == np.sign(ics[2])
    print(f"{f:14s} {ics[0]:+8.3f} {ics[1]:+8.3f} {ics[2]:+8.3f} {noise:7.3f}  {'CONSISTENT: lead' if ok else 'noise / unstable'}")
print("\nfeatures use only past data; 7 features tested, so one 'lead' out of 7 at 2-sigma is expected by chance about 0.3 times")

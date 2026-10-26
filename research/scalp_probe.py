"""Triple-barrier baseline on 1m candles: how often does +TP hit before -SL, and what is left after fees?"""
import json, sys, time, urllib.request

def fetch(inst, bars):
    out, after = [], ""
    while len(out) < bars:
        url = f"https://www.okx.com/api/v5/market/history-candles?instId={inst}&bar=1m&limit=100" + (f"&after={after}" if after else "")
        rows = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["data"]
        if not rows: break
        out += rows; after = rows[-1][0]; time.sleep(0.12)
    return [(float(r[2]), float(r[3]), float(r[4])) for r in reversed(out)]  # high, low, close

def barrier(c, tp, sl, horizon):
    wins = losses = timeouts = 0; tmo_ret = 0.0
    for i in range(len(c) - horizon):
        e = c[i][2]
        for h, l, cl in c[i+1:i+1+horizon]:
            if l <= e*(1-sl): losses += 1; break      # stop checked first (conservative)
            if h >= e*(1+tp): wins += 1; break
        else:
            timeouts += 1; tmo_ret += c[i+horizon][2]/e - 1
    n = wins + losses + timeouts
    return n, wins/n, losses/n, timeouts/n, (tmo_ret/timeouts if timeouts else 0)

for inst in sys.argv[1:]:
    c = fetch(inst, 10000)
    print(f"\n{inst}: {len(c)} bars")
    for tp, sl in [(.003,.003),(.003,.0015),(.003,.006),(.002,.002)]:
        n, w, l, t, tr = barrier(c, tp, sl, 30)
        gross = w*tp - l*sl + t*tr
        print(f"TP {tp:.2%} SL {sl:.2%} 30m | win {w:.1%} loss {l:.1%} timeout {t:.1%} | gross/trade {gross:+.4%} | after 0.20% rt fee {gross-.002:+.4%} | after 0.08% maker rt {gross-.0008:+.4%}")

"""Alpha's Gate testnet bot. It trades ONLY analyst calls; no hand-picked trades.
  python research/gate_bot.py run      run the analyst, take its calls through the filters, open trades, log the reasons
  python research/gate_bot.py manage   close trades past their horizon, record outcomes
  python research/gate_bot.py review   print every trade: what, why, result
Testnet is treated as real money: sizing, stops and limits are the live rules, except risk is cut to EXPLORE_RISK_PCT because no setup
is proven yet (see BACKFILL.md). Trades are evidence-gathering, and the judge's gate decides if anything ever goes live."""
import json, subprocess, sys, time, urllib.error
from pathlib import Path
import gate_analyst as A, gate_trader as T

LOG = A.PRIVATE / "trades.jsonl"
EXPLORE_RISK_PCT = 0.25
BLOCKED = {"setup_pullback": "negative in the second half of history (-1.45% mean, 30 calls): the data rejects it"}
WHY = {"setup_trend": "price above SMA50 above SMA200 with RSI 50-70: an uptrend that is not overheated",
       "setup_breakdown": "price below SMA200 and SMA50 with RSI above 40: a downtrend with room left to fall"}

def read(p): return [json.loads(x) for x in open(p)] if Path(p).exists() else []

def todays_calls():
    subprocess.run([sys.executable, str(Path(__file__).parent / "gate_analyst.py")], check=True)
    rows = read(A.PRIVATE / "calls.jsonl"); last = max(r["ts"] for r in rows)
    return [r for r in rows if r["ts"] == last and r["call"] != "flat"]

def run():
    held = {t["coin"] for t in read(LOG) if "closed" not in t}
    for c in todays_calls():
        setup = next((t for t in c["tags"] if t.startswith("setup_")), None)
        if setup in BLOCKED: print(f"skip {c['coin']} {c['call']}: {setup} blocked: {BLOCKED[setup]}"); continue
        if c["coin"] in held: print(f"skip {c['coin']}: already holding"); continue
        try: r = T.open_trade(c["coin"], c["call"], c["stop_pct"], c["target_pct"], {"risk_pct": EXPLORE_RISK_PCT})
        except SystemExit as e: print(f"skip {c['coin']}: {e}"); continue
        except ValueError as e: print(f"skip {c['coin']}: {e}"); continue
        except urllib.error.HTTPError as e: print(f"skip {c['coin']}: Gate refused the order: {e.read().decode()[:120]}"); continue
        rec = {"opened": int(time.time()), "coin": c["coin"], "side": c["call"], "setup": setup, "tags": c["tags"], "why": WHY.get(setup, ""),
               "horizon_h": c["horizon_h"], "fill": r["fill_price"], "stop": r["stop"], "target": r["target"], "contracts": r["contracts"],
               "risk_usd": r["risk_usd"], "notional": r["notional"]}
        with open(LOG, "a") as f: f.write(json.dumps(rec) + "\n")
        print(f"OPEN {rec['side']} {rec['coin']} {rec['contracts']} @ {rec['fill']} stop {rec['stop']} target {rec['target']} risk ${rec['risk_usd']} | {rec['why']}")

def manage():
    trades = read(LOG); open_pos = {p["contract"] for p in T.api("GET", "/futures/usdt/positions") if float(p["size"])}
    for t in trades:
        if "closed" in t: continue
        if t["coin"] in open_pos and time.time() < t["opened"] + t["horizon_h"] * 3600: continue
        if t["coin"] in open_pos: T.close_trade(t["coin"]); t["exit"] = "horizon"
        else: t["exit"] = "stop_or_target"
        T.api("DELETE", "/futures/usdt/price_orders", f"contract={t['coin']}")  # remove the leftover stop/target
        res = [x for x in T.api("GET", "/futures/usdt/position_close", f"contract={t['coin']}&limit=5") if x["time"] >= t["opened"]]
        t["pnl_usd"] = round(sum(float(x["pnl"]) for x in res), 4); t["closed"] = int(time.time())
        print(f"CLOSED {t['coin']} {t['exit']} pnl ${t['pnl_usd']}")
    LOG.write_text("".join(json.dumps(t) + "\n" for t in trades))

def review():
    for t in read(LOG):
        res = f"{t['exit']} pnl ${t['pnl_usd']}" if "closed" in t else "open"
        print(f"{time.strftime('%m-%d %H:%M', time.gmtime(t['opened']))} {t['side']:5s} {t['coin']:10s} risk ${t['risk_usd']} -> {res}\n   why: {t['why']}  [{', '.join(t['tags'])}]")

if __name__ == "__main__":
    {"run": run, "manage": manage, "review": review}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()

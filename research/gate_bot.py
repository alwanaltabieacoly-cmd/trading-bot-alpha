"""Alpha's Gate testnet bot. It trades ONLY analyst calls; no hand-picked trades.
  python research/gate_bot.py run      run the analyst, take its calls through the filters, open trades, log the reasons
  python research/gate_bot.py manage   close trades past their horizon, record outcomes
  python research/gate_bot.py review   print every trade: what, why, result
  python research/gate_bot.py daily    once per UTC day: manage, score the judge, run, send the Telegram summary (what the GitHub workflow calls)
  python research/gate_bot.py status   which setups may trade, at what risk, and whether a halt is active
  python research/gate_bot.py resume   clear a drawdown halt after you have looked at why
Testnet is treated as real money: sizing, stops and limits are the live rules, except risk is cut to EXPLORE_RISK_PCT because no setup
is proven yet (see BACKFILL.md). Trades are evidence-gathering, and the judge's gate decides if anything ever goes live."""
import contextlib, io, json, subprocess, sys, time, urllib.error
from pathlib import Path
import gate_config, gate_lock, gate_alpha as G, gate_analyst as A, gate_judge as J, gate_notify as N, gate_trader as T

LOG = A.PRIVATE / "trades.jsonl"; SCORED = A.PRIVATE / "scored.jsonl"; BACKFILL = A.PRIVATE / "backfill_rows.jsonl"
CFG = gate_config.CFG    # limits live in config/gate.json
EXPLORE_RISK_PCT, GRACE_H = CFG["explore_risk_pct"], CFG["grace_h"]
ALPHA_MAX_PER_DAY = CFG["alpha_max_trades_per_day"]
DAILY_LOSS_PCT = CFG["daily_loss_pct"]    # realised loss today beyond this % of equity: no new trades until the next UTC day
DRAWDOWN_PCT = CFG["drawdown_pct"]        # equity this far under its peak: halt until a human runs `resume`
EXPLORE_DAYS, PROVEN_DAYS = CFG["explore_days"], CFG["proven_days"]
HALT = A.PRIVATE / "HALT.txt"; EQUITY = A.PRIVATE / "equity.json"
WHY = {"setup_trend": "price above SMA50 above SMA200 with RSI 50-70: an uptrend that is not overheated",
       "setup_breakdown": "price below SMA200 and SMA50 with RSI above 40: a downtrend with room left to fall"}

def read(p): return [json.loads(x) for x in open(p)] if Path(p).exists() else []

def setup_status(setup, backfill, live):
    """The auto-gate. Returns (state, risk_pct, reason). Live-scored calls are out of sample, so they outrank the backfill.
    <10 live days: the backfill mean decides.  10-29: live mean decides, explore risk.  30+ and Wilson lower bound >50% and beats hold: full risk."""
    if not setup: return "blocked", 0.0, "no named setup"
    mean = lambda xs: sum(xs) / len(xs)
    by_day = {}
    for r in live:
        if setup in r["tags"]: by_day.setdefault(r["day"], []).append(r)
    net = [mean([r["net"] for r in rs]) for rs in by_day.values()]; base = [mean([r["base"] for r in rs]) for rs in by_day.values()]
    n = len(net)
    if n >= PROVEN_DAYS:
        lower = J.wilson_lower(sum(x > 0 for x in net), n)
        if lower > 0.5 and mean(net) > mean(base): return "proven", T.LIMITS["risk_pct"], f"live {n} days, 95% lower bound {lower:.0%}, mean {mean(net):+.3f}% vs hold {mean(base):+.3f}%"
    if n >= EXPLORE_DAYS:
        ok = mean(net) > 0; return ("explore", EXPLORE_RISK_PCT, f"live {n} days, mean {mean(net):+.3f}%") if ok else ("blocked", 0.0, f"live {n} days, mean {mean(net):+.3f}% is not positive")
    bf = [r["net"] for r in backfill if setup in r["tags"]]
    if not bf: return "blocked", 0.0, "no evidence yet"
    return ("explore", EXPLORE_RISK_PCT, f"backfill {len(bf)} calls, mean {mean(bf):+.3f}% (live {n} days so far)") if mean(bf) > 0 else \
           ("blocked", 0.0, f"backfill {len(bf)} calls, mean {mean(bf):+.3f}% is not positive")

def check_halt(trades, equity, peak, today):
    """Returns a reason to stop opening trades, or None. trades: log rows; today: 'YYYY-MM-DD' (UTC)."""
    if peak and equity < peak * (1 - DRAWDOWN_PCT / 100): return f"drawdown halt: equity {equity:.2f} is {100 * (1 - equity / peak):.1f}% under the peak {peak:.2f}"
    lost = -sum(t.get("pnl_usd", 0) for t in trades if "closed" in t and time.strftime("%Y-%m-%d", time.gmtime(t["closed"])) == today)
    if lost > equity * DAILY_LOSS_PCT / 100: return f"daily loss halt: lost ${lost:.2f} today, limit ${equity * DAILY_LOSS_PCT / 100:.2f}"
    return None

def equity_now():
    e = float(T.api("GET", "/futures/usdt/accounts")["total"]); peak = json.loads(EQUITY.read_text())["peak"] if EQUITY.exists() else e
    if not EQUITY.exists() or e > peak: EQUITY.write_text(json.dumps({"peak": max(peak, e), "equity": e, "ts": int(time.time())}))  # only the peak is read back; writing on every read kept the repo dirty
    return e, max(peak, e)

def todays_calls():
    subprocess.run([sys.executable, str(Path(__file__).parent / "gate_analyst.py")], check=True)
    rows = read(A.PRIVATE / "calls.jsonl"); last = max(r["ts"] for r in rows)
    return [r for r in rows if r["ts"] == last and r["call"] != "flat"]

def run():
    trades = read(LOG); held = {t["coin"] for t in trades if "closed" not in t}
    if HALT.exists(): print(f"HALTED, no new trades: {HALT.read_text().strip()} (run `gate_bot.py resume` after review)"); return
    equity, peak = equity_now(); why = check_halt(trades, equity, peak, time.strftime("%Y-%m-%d", time.gmtime()))
    if why:
        if why.startswith("drawdown"): HALT.write_text(why)
        print(f"HALTED, no new trades: {why}"); return
    backfill, live = read(BACKFILL), read(SCORED); status = {}
    for c in todays_calls():
        setup = next((t for t in c["tags"] if t.startswith("setup_")), None)
        state, risk, reason = status[setup] = status.get(setup) or setup_status(setup, backfill, live)
        if state == "blocked": print(f"skip {c['coin']} {c['call']}: {setup} blocked: {reason}"); continue
        if c["coin"] in held: print(f"skip {c['coin']}: already holding"); continue
        try: r = T.open_trade(c["coin"], c["call"], c["stop_pct"], c["target_pct"], {"risk_pct": risk})
        except SystemExit as e: print(f"skip {c['coin']}: {e}"); continue
        except ValueError as e: print(f"skip {c['coin']}: {e}"); continue
        except urllib.error.HTTPError as e: print(f"skip {c['coin']}: Gate refused the order: {e.read().decode()[:120]}"); continue
        rec = {"opened": int(time.time()), "coin": c["coin"], "side": c["call"], "setup": setup, "tags": c["tags"], "why": WHY.get(setup, ""),
               "horizon_h": c["horizon_h"], "fill": r["fill_price"], "stop": r["stop"], "target": r["target"], "contracts": r["contracts"],
               "risk_usd": r["risk_usd"], "notional": r["notional"], "gate": f"{state}: {reason}"}
        with open(LOG, "a") as f: f.write(json.dumps(rec) + "\n")
        print(f"OPEN {rec['side']} {rec['coin']} {rec['contracts']} @ {rec['fill']} stop {rec['stop']} target {rec['target']} risk ${rec['risk_usd']} | {rec['why']} | gate {rec['gate']}")

def manage():
    trades = read(LOG); open_pos = {p["contract"] for p in T.api("GET", "/futures/usdt/positions") if float(p["size"])}
    for t in trades:
        if "closed" in t: continue
        if t["coin"] in open_pos and time.time() < t["opened"] + (t["horizon_h"] - GRACE_H) * 3600: continue  # the daily run can start minutes before the horizon: without grace a trade would sit another full day
        if t["coin"] in open_pos: T.close_trade(t["coin"]); t["exit"] = t.pop("close_reason", "horizon")
        else: t["exit"] = "stop_or_target"
        T.api("DELETE", "/futures/usdt/price_orders", f"contract={t['coin']}")  # remove the leftover stop/target
        res = [x for x in T.api("GET", "/futures/usdt/position_close", f"contract={t['coin']}&limit=5") if x["time"] >= t["opened"]]
        t["pnl_usd"] = round(sum(float(x["pnl"]) for x in res), 4); t["closed"] = int(max((x["time"] for x in res), default=time.time()))   # Gate's own close time, so a loss lands on the right UTC day
        print(f"CLOSED {t['coin']} {t['exit']} pnl ${t['pnl_usd']}")
    LOG.write_text("".join(json.dumps(t) + "\n" for t in trades))

def alpha_trades_left():
    today = G.day_key(time.time())
    return max(0, ALPHA_MAX_PER_DAY - sum(1 for r in G._rows(G.FILE) if r["source"] == "alpha" and r["day"] == today and r["call"] != "flat"))

def alpha_trade(coin, side, stop_pct, target_pct, why, tags=()):
    """Alpha's own trade. Logged as an Alpha call first (the judge scores it whatever happens), then opened at EXPLORE_RISK_PCT through the same
    halts, sizing, stop and target as the bot's trades. Alpha cannot raise its risk or clear a halt. Raises ValueError with the reason if refused."""
    if side not in ("long", "short"): raise ValueError("side must be long or short")
    try: manage()    # book stopped-out trades first, so today's realised loss is complete before the daily-loss check
    except Exception as e: raise ValueError(f"cannot reconcile Gate trades, so the daily-loss check would be incomplete: {e}")
    trades = read(LOG)
    if HALT.exists(): raise ValueError(f"halted: {HALT.read_text().strip()} (a human must run `gate_bot.py resume`)")
    equity, peak = equity_now(); stop = check_halt(trades, equity, peak, time.strftime("%Y-%m-%d", time.gmtime()))
    if stop:
        if stop.startswith("drawdown"): HALT.write_text(stop)
        raise ValueError(f"halted: {stop}")
    if any(t["coin"] == coin and "closed" not in t for t in trades): raise ValueError(f"already holding {coin}")
    if not alpha_trades_left():
        raise ValueError(f"daily limit: Alpha already made {ALPHA_MAX_PER_DAY} long/short calls for this UTC day (config alpha_max_trades_per_day)")
    G.make_call(coin, side, stop_pct, target_pct, why, tags)
    try: r = T.open_trade(coin, side, stop_pct, target_pct, {"risk_pct": EXPLORE_RISK_PCT})
    except SystemExit as e: raise ValueError(f"call logged for scoring, trade not opened: {e}")
    except urllib.error.HTTPError as e: raise ValueError(f"call logged for scoring, Gate refused the order: {e.read().decode()[:120]}")
    rec = {"opened": int(time.time()), "coin": coin, "side": side, "setup": "alpha", "tags": ["alpha", *tags], "why": why.strip()[:600],
           "horizon_h": A.HORIZON_H, "fill": r["fill_price"], "stop": r["stop"], "target": r["target"], "contracts": r["contracts"],
           "risk_usd": r["risk_usd"], "notional": r["notional"], "gate": f"alpha: explore risk {EXPLORE_RISK_PCT}% until the versus scoreboard proves it"}
    with open(LOG, "a") as f: f.write(json.dumps(rec) + "\n")
    return rec

def alpha_close(coin, why="manual"):
    """Close one of Alpha's own open trades now and record the result. Only trades opened by alpha_trade."""
    trades = read(LOG); t = next((t for t in trades if t["coin"] == coin and t.get("setup") == "alpha" and "closed" not in t), None)
    if not t: raise ValueError(f"no open Alpha trade on {coin}")
    t["horizon_h"] = 0; t["close_reason"] = f"alpha: {why.strip()[:200]}"
    LOG.write_text("".join(json.dumps(x) + "\n" for x in trades)); manage()
    return next(x for x in read(LOG) if x["coin"] == coin and x["opened"] == t["opened"])

def review():
    for t in read(LOG):
        res = f"{t['exit']} pnl ${t['pnl_usd']}" if "closed" in t else "open"
        print(f"{time.strftime('%m-%d %H:%M', time.gmtime(t['opened']))} {t['side']:5s} {t['coin']:10s} risk ${t['risk_usd']} -> {res}\n   why: {t['why']}  [{', '.join(t['tags'])}]")

def status():
    backfill, live = read(BACKFILL), read(SCORED)
    for setup in sorted({t for r in backfill + live for t in r["tags"] if t.startswith("setup_")}):
        state, risk, reason = setup_status(setup, backfill, live); print(f"{setup:18s} {state:8s} risk {risk}%  {reason}")
    eq, peak = equity_now(); print(f"equity {eq:.2f}, peak {peak:.2f}; " + (f"HALT: {HALT.read_text().strip()}" if HALT.exists() else "no halt") +
        f"; today: {check_halt(read(LOG), eq, peak, time.strftime('%Y-%m-%d', time.gmtime())) or 'within limits'}")

def resume():
    HALT.unlink(missing_ok=True); e = float(T.api("GET", "/futures/usdt/accounts")["total"]); EQUITY.write_text(json.dumps({"peak": e, "equity": e, "ts": int(time.time())})); print(f"halt cleared; peak reset to {e:.2f}")

def daily():
    A.PRIVATE.mkdir(parents=True, exist_ok=True); stamp = A.PRIVATE / "last_daily.txt"; today = time.strftime("%Y-%m-%d", time.gmtime())
    if stamp.exists() and stamp.read_text().strip() == today: print(f"already ran for {today}"); return
    buf = io.StringIO()
    with gate_lock.held("daily", wait_s=420), contextlib.redirect_stdout(buf):    # Alpha on the PC may be mid-trade
        manage()
        print(subprocess.run([sys.executable, str(Path(__file__).parent / "gate_judge.py"), "live"], check=True, capture_output=True, text=True).stdout.strip())
        run()
    out = buf.getvalue(); print(out); stamp.write_text(today)
    lines = [l[:300] for l in out.splitlines() if l.startswith(("OPEN", "CLOSED", "HALT", "skip", "scored", "VERSUS"))]
    N.send(f"Alpha {today}\n" + ("\n".join(lines) or "nothing to report"))

if __name__ == "__main__":
    {"run": run, "manage": manage, "review": review, "daily": daily, "status": status, "resume": resume}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()

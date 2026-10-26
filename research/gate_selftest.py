"""End-to-end self-test of the Gate bot against the real TESTNET (fake money). Uses the bot's own code with a throwaway state folder and checks
outcomes on Gate itself (positions, triggers, P&L), not just that nothing crashed. Places one small BTC trade and closes it.
  python research/gate_selftest.py                      run everything; exit 1 on any FAIL
  python research/gate_selftest.py --require-telegram   a missing Telegram config is a FAIL, not a SKIP (use on GitHub)
Needs the testnet key (env GATE_TESTNET_KEY/SECRET or Credential Manager). Never touches the live key."""
import contextlib, io, json, os, sys, tempfile, time, traceback
from pathlib import Path
TMP = tempfile.mkdtemp(prefix="alpha-selftest-"); os.environ["ALPHA_STATE_DIR"] = TMP
sys.path.insert(0, str(Path(__file__).parent))
import shutil
import gate_analyst as A, gate_bot as B, gate_notify as N, gate_trader as T
shutil.copy(Path(__file__).parent / "gate_state" / "backfill_rows.jsonl", TMP)   # the auto-gate needs the same evidence the real bot has

COIN = "BTC_USDT"; REQUIRE_TG = "--require-telegram" in sys.argv
CALL = {"coin": COIN, "call": "long", "tags": ["above_sma200", "above_sma50", "setup_trend"], "stop_pct": 1.0, "target_pct": 2.0, "horizon_h": 24}
results, ctx = [], {}

class Skip(Exception): pass
def check(name):
    def deco(fn):
        try: fn(); results.append((name, "PASS", ""))
        except Skip as e: results.append((name, "SKIP", str(e)))
        except AssertionError as e: results.append((name, "FAIL", str(e)))
        except Exception as e: results.append((name, "FAIL", f"{type(e).__name__}: {str(e)[:150]}")); traceback.print_exc(limit=2)
    return deco
def need(ok, msg): 
    if not ok: raise AssertionError(msg)
def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): fn(*a)
    return buf.getvalue()
def position(): return next((float(p["size"]) for p in T.api("GET", "/futures/usdt/positions") if p["contract"] == COIN), 0.0)
def triggers(): return T.api("GET", "/futures/usdt/price_orders", f"status=open&contract={COIN}")
def equity(): return float(T.api("GET", "/futures/usdt/accounts")["total"])
def rows(): return B.read(B.LOG)
def calls(*c): B.todays_calls = lambda: list(c)
def reset_state():
    for f in (B.HALT, B.EQUITY): f.unlink(missing_ok=True)

@check("1 testnet key works, account funded")
def _(): ctx["eq0"] = equity(); need(ctx["eq0"] > 100, f"equity {ctx['eq0']}")

@check("2 clean slate: no BTC position or triggers (else the test would disturb the real bot)")
def _():
    need(position() == 0 and not triggers(), f"BTC position {position()} / {len(triggers())} triggers already exist: the real bot holds BTC, test aborted")
if results[-1][1] == "FAIL": print("clean slate failed: stopping before any order"); results.append(("(rest)", "SKIP", "aborted")); REST = False
else: REST = True

if REST:
    @check("3 setup the auto-gate blocks opens nothing")
    def _():
        reset_state(); calls({**CALL, "tags": ["above_sma200", "below_sma20", "setup_pullback"]}); out = quiet(B.run)
        need("blocked" in out and position() == 0 and not rows(), out[-200:])

    @check("4 call with no named setup opens nothing")
    def _():
        calls({**CALL, "tags": ["above_sma200"]}); out = quiet(B.run); need(position() == 0 and not rows(), out[-200:])

    @check("5 allowed call opens: position, stop and target on Gate match the log")
    def _():
        ctx["eq1"] = equity(); calls(CALL); out = quiet(B.run); r = rows(); need(len(r) == 1, f"{len(r)} rows: {out[-200:]}")
        t = r[0]; need(position() > 0 and position() == t["contracts"], f"position {position()} vs logged {t['contracts']}")
        trig = triggers(); need(len(trig) == 2, f"{len(trig)} triggers on Gate")
        rules = {x["trigger"]["rule"]: float(x["trigger"]["price"]) for x in trig}
        need(set(rules) == {1, 2}, f"rules {set(rules)}"); stop, target = rules[2], rules[1]
        need(abs(stop - float(t["stop"])) / stop < 1e-4 and abs(target - float(t["target"])) / target < 1e-4, f"stop {stop}/{t['stop']} target {target}/{t['target']}")
        need(stop < float(t["fill"]) < target, "stop and target are not on the right sides of the fill")
        need(t["risk_usd"] <= ctx["eq1"] * B.EXPLORE_RISK_PCT / 100 * 1.01, f"risk ${t['risk_usd']} over {B.EXPLORE_RISK_PCT}% of {ctx['eq1']:.0f}")
        need(t["gate"].startswith("explore") and t["why"], f"gate/why not recorded: {t.get('gate')!r}")

    @check("6 same coin again: no second position")
    def _(): 
        before = position(); calls(CALL); quiet(B.run); need(position() == before and len(rows()) == 1, f"position {before} -> {position()}")

    @check("7 manage keeps a trade before its horizon")
    def _(): quiet(B.manage); need(position() > 0 and "closed" not in rows()[0], "closed too early")

    @check("8 manage closes at the horizon: flat, no leftover triggers, P&L matches the account")
    def _():
        r = rows(); r[0]["horizon_h"] = 1; B.LOG.write_text("".join(json.dumps(x) + "\n" for x in r)); quiet(B.manage); t = rows()[0]
        need("closed" in t and t["exit"] == "horizon", f"row {t.get('exit')}"); need(position() == 0, f"position {position()} left open")
        need(not triggers(), f"{len(triggers())} triggers left"); delta = equity() - ctx["eq1"]
        need(abs(delta - t["pnl_usd"]) < 0.15, f"logged pnl {t['pnl_usd']} vs account change {delta:+.4f}")
        ctx["pnl"] = t["pnl_usd"]

    @check("9 daily-loss halt stops new trades")
    def _():
        before = B.LOG.read_text(); B.LOG.write_text(before + json.dumps({"coin": "X", "closed": int(time.time()), "pnl_usd": -50}) + "\n")
        calls(CALL); out = quiet(B.run); n = len(rows()); B.LOG.write_text(before)
        need("daily loss halt" in out and position() == 0 and n == 2, out[-200:])

    @check("10 drawdown halt writes HALT, persists, and `resume` clears it")
    def _():
        e = equity(); B.EQUITY.write_text(json.dumps({"peak": e * 1.2, "equity": e, "ts": 0})); calls(CALL); out = quiet(B.run)
        need("drawdown halt" in out and B.HALT.exists() and position() == 0, out[-200:])
        B.EQUITY.write_text(json.dumps({"peak": e, "equity": e, "ts": 0})); need("HALTED" in quiet(B.run) and position() == 0, "halt did not persist after equity recovered")
        quiet(B.resume); need(not B.HALT.exists() and abs(json.loads(B.EQUITY.read_text())["peak"] - e) < 5, "resume did not clear")

    @check("11 judge scores a finished call on real candles")
    def _():
        mark = float(T.public(f"/futures/usdt/contracts/{COIN}")["mark_price"]); ts = int(time.time()) - 30 * 3600
        (A.PRIVATE / "calls.jsonl").write_text(json.dumps({**CALL, "ts": ts, "day": ts // 86400 * 86400, "entry": mark}) + "\n")
        import subprocess; out = subprocess.run([sys.executable, str(Path(__file__).parent / "gate_judge.py"), "live"], capture_output=True, text=True).stdout
        s = B.read(A.PRIVATE / "scored.jsonl"); need(len(s) == 1 and s[0]["out"] in ("stop", "target", "timeout") and isinstance(s[0]["net"], float), out[-200:])

    @check("12 daily() runs once per UTC day and sends the Telegram summary")
    def _():
        if not N.creds()[0]: raise AssertionError("Telegram not configured") if REQUIRE_TG else Skip("Telegram not configured")
        calls(); buf = io.StringIO()
        with contextlib.redirect_stdout(buf): B.daily(); B.daily()
        out = buf.getvalue(); need("telegram sent (message_id" in out, "Telegram did not confirm: " + out[-200:]); need("already ran for" in out, "second daily() was not blocked")

    @check("13 Telegram confirms a message (Telegram's own message_id)")
    def _():
        if not N.creds()[0]: raise AssertionError("Telegram not configured") if REQUIRE_TG else Skip("Telegram not configured")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): ok = N.send("Alpha self-test: Telegram path works")
        need(ok and "message_id" in buf.getvalue(), buf.getvalue())

@check("14 collector data is fresh (newest row under 3 h old)")
def _():
    files = sorted((Path(__file__).parent / "gate_data").glob("*.csv"))
    if not files: raise Skip("no collector data in this checkout")
    last = int(open(files[-1]).read().strip().splitlines()[-1].split(",")[0]) * 60; age = (time.time() - last) / 3600
    need(age < 3, f"newest collector row is {age:.1f} h old: the collector has stopped")

@check("15 nothing left behind on the account")
def _():
    if position(): T.close_trade(COIN)
    need(position() == 0 and not triggers(), "leftover position or triggers (cleaned up now)")

passed = sum(r[1] == "PASS" for r in results); failed = [r for r in results if r[1] == "FAIL"]
for n, s, m in results: print(f"{s:5s} {n}" + (f"   <- {m}" if m else ""))
line = f"{passed} pass, {len(failed)} fail, {sum(r[1] == 'SKIP' for r in results)} skip" + (f"; test trade P&L {ctx['pnl']:+.4f} USDT" if "pnl" in ctx else "")
print("\n" + line)
N.send(("Alpha self-test FAILED: " + "; ".join(n for n, _, _ in failed) if failed else "Alpha self-test OK: ") + f"\n{line}")
sys.exit(1 if failed else 0)

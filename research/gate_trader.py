"""Gate USDT-perp trader. TESTNET ONLY: refuses any other environment.
Every entry gets a stop-loss trigger order; if the stop cannot be placed and read back, the position is closed at once.
Every order is read back from Gate and compared with what was intended. Sizing risks a fixed % of equity to the stop.
Gate field meanings (gateapi-python docs): size>0 long / <0 short; price "0"+tif ioc = market; trigger rule 1 = price >= trigger, 2 = price <= trigger;
price_type 1 = mark price; order_type close-long-position / close-short-position close the whole position.
Untested against a live testnet until a testnet key is stored (see gate_auth.py set testnet)."""
from decimal import Decimal
import json, math, urllib.request
import gate_auth as g

ENV = "testnet"
LIMITS = {"risk_pct": 1.0, "max_notional_x_equity": 3.0, "max_open": 3, "max_leverage": 3}

def public(path):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.gateio.ws/api/v4" + path, headers={"User-Agent": "alpha"}), timeout=15))

def api(method, path, query="", body=None):
    return g.call(method, path, query, json.dumps(body, separators=(",", ":")) if body is not None else "", env=ENV)

def round_to(x, step):
    """Nearest multiple of step, exact in decimal: float math gives 79364.90000000001 for 793649 * 0.1, which Gate rejects."""
    d = Decimal(str(step)); return float((Decimal(str(x)) / d).to_integral_value() * d)
def fmt(x): return f"{Decimal(repr(float(x))).normalize():f}"  # plain decimals, never 4.2e-06

def plan(contract, side, entry, stop_pct, target_pct, equity, spec, limits=None):
    """Pure function: returns an order plan or raises ValueError with the reason. side: 'long'|'short'."""
    L = {**LIMITS, **(limits or {})}
    if side not in ("long", "short"): raise ValueError("side must be long or short")
    if not 0 < stop_pct <= 10: raise ValueError("stop_pct must be in (0, 10] percent: a stop is mandatory")
    if target_pct <= 0: raise ValueError("target_pct must be > 0")
    q, step = float(spec["quanto_multiplier"]), float(spec["order_price_round"])
    risk_usd = equity * L["risk_pct"] / 100
    loss_per_contract = entry * stop_pct / 100 * q
    n = math.floor(risk_usd / loss_per_contract)
    n = min(n, math.floor(equity * L["max_notional_x_equity"] / (entry * q)))
    if n < int(spec["order_size_min"]): raise ValueError(f"size {n} below minimum {spec['order_size_min']}: risking ${risk_usd:.2f} to a {stop_pct}% stop buys less than one contract")
    sgn = 1 if side == "long" else -1
    stop = round_to(entry * (1 - sgn * stop_pct / 100), step); tp = round_to(entry * (1 + sgn * target_pct / 100), step)
    notional = n * q * entry
    return {"contract": contract, "side": side, "contracts": n, "size": sgn * n, "entry_ref": entry, "stop": stop, "target": tp,
            "risk_usd": round(n * loss_per_contract, 4), "notional": round(notional, 2), "margin_at_max_lev": round(notional / L["max_leverage"], 2), "rr": round(target_pct / stop_pct, 2)}

def trigger_body(contract, side, price, kind):
    """Close-whole-position trigger. kind 'stop'|'target'. Long stop fires at price <= p (rule 2); long target at >= p (rule 1); reversed for shorts."""
    long = side == "long"; rule = 2 if (kind == "stop") == long else 1
    return {"initial": {"contract": contract, "size": 0, "price": "0", "close": True, "tif": "ioc", "reduce_only": True, "text": "api"},
            "trigger": {"strategy_type": 0, "price_type": 1, "price": fmt(price), "rule": rule, "expiration": 86400 * 7},
            "order_type": "close-long-position" if long else "close-short-position"}

def open_trade(contract, side, stop_pct, target_pct, limits=None):
    L = {**LIMITS, **(limits or {})}
    acct = api("GET", "/futures/usdt/accounts"); equity = float(acct["total"])
    if equity <= 0: raise SystemExit("testnet account has no funds: claim virtual USDT on the Gate futures testnet page")
    open_pos = [p for p in api("GET", "/futures/usdt/positions") if float(p["size"]) != 0]
    if len(open_pos) >= L["max_open"]: raise SystemExit(f"max_open {L['max_open']} reached")
    if any(p["contract"] == contract for p in open_pos): raise SystemExit(f"{contract} already has a position")
    book = api("GET", "/futures/usdt/order_book", f"contract={contract}&limit=1")["asks" if side == "long" else "bids"]
    if not book: raise SystemExit(f"{contract} testnet book has no {'asks' if side == 'long' else 'bids'}: a market order would be refused (CONTRACT_NO_COUNTER)")
    spec = public(f"/futures/usdt/contracts/{contract}"); entry = float(spec["mark_price"])
    p = plan(contract, side, entry, stop_pct, target_pct, equity, spec, limits)
    lev = max(1, min(L["max_leverage"], int(float(spec["leverage_max"]))))
    api("POST", f"/futures/usdt/positions/{contract}/leverage", f"leverage={lev}")
    o = api("POST", "/futures/usdt/orders", body={"contract": contract, "size": p["size"], "price": "0", "tif": "ioc", "text": "t-alpha"})
    back = api("GET", f"/futures/usdt/orders/{o['id']}")
    if back.get("status") != "finished" or int(back.get("left", 1)) != 0:
        raise SystemExit(f"entry not fully filled: status={back.get('status')} left={back.get('left')} finish_as={back.get('finish_as')}")
    fill = float(back["fill_price"])
    try:
        ids = {k: api("POST", "/futures/usdt/price_orders", body=trigger_body(contract, side, p[k], k))["id"] for k in ("stop", "target")}
        for k, i in ids.items():
            r = api("GET", f"/futures/usdt/price_orders/{i}")
            if r.get("status") != "open" or float(r["trigger"]["price"]) != p[k]: raise RuntimeError(f"{k} order read back as {r.get('status')} {r['trigger']}")
    except Exception as e:  # never leave a position without a stop
        api("POST", "/futures/usdt/orders", body={"contract": contract, "size": 0, "price": "0", "close": True, "tif": "ioc", "text": "t-alpha-abort"})
        api("DELETE", "/futures/usdt/price_orders", f"contract={contract}")
        raise SystemExit(f"stop/target failed, position closed: {e}")
    return {**p, "fill_price": fill, "order_id": o["id"], "trigger_ids": ids}

def close_trade(contract):
    api("POST", "/futures/usdt/orders", body={"contract": contract, "size": 0, "price": "0", "close": True, "tif": "ioc", "text": "t-alpha-close"})
    api("DELETE", "/futures/usdt/price_orders", f"contract={contract}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 5 and sys.argv[1] == "plan":  # offline sizing preview: plan CONTRACT side stop% target% equity
        c, side, s, t, eq = sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
        spec = public(f"/futures/usdt/contracts/{c}"); print(json.dumps(plan(c, side, float(spec["mark_price"]), s, t, eq, spec), indent=1))
    else: print("usage: gate_trader.py plan BTC_USDT long 1.0 2.0 1000")

# TradingView webhook bridge + paper broker
# Receives TV alerts, validates, logs, and executes on paper broker.
# No real money. No live exchange keys.

from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json, hmac, hashlib, os
from typing import Optional

app = FastAPI(title="TradingView Bridge")

# ---------- config ----------
WEBHOOK_SECRET = os.getenv("TV_WEBHOOK_SECRET", "change-me")
PAPER_STATE_PATH = Path("user_data/paper_broker/state.json")
DECISIONS_PATH = Path("reports/decisions")
LATEST_DECISION_PATH = Path("user_data/decisions/latest.json")
LOG_PATH = Path("user_data/paper_broker/trades.jsonl")

# ---------- models ----------
class TVAlert(BaseModel):
    symbol: str
    action: str = Field(..., pattern="^(buy|sell|close)$")
    price: float
    timeframe: str = "1D"
    strategy: str = "sma200"
    confidence: float = 0.5
    secret: str = ""


# --- strategy-aware routing -----------------------------------------------
# Two strategy families:
#   sma200  - crypto trend-following (BTC/ETH/SOL/BNB/XRP, 1D/4H)
#   scalp   - equity mean-reversion (AAPL, 1M) from TradingView chart work
# Crypto uses the multi-agent deliberation gate. Equity uses a built-in
# guard (daily loss limit + known strategy) since there is no deliberation
# cycle for equities yet.
SCALP_STRATEGIES = {"aapl_scalp_trend", "aapl_scalp_reversion", "scalp"}
EQUITY_SYMBOLS = {"AAPL", "MSFT", "GOOG", "TSLA", "SPY", "QQQ"}
SCALP_DAILY_LOSS_LIMIT = 5.0


def _is_equity(alert):
    sym = alert.symbol.upper()
    return sym in EQUITY_SYMBOLS or "/" not in sym


def _scalp_guard(state, alert):
    if alert.strategy not in SCALP_STRATEGIES:
        return False, f"unknown scalp strategy: {alert.strategy}"
    today = datetime.now(timezone.utc).date().isoformat()
    daily_pnl = 0.0
    if LOG_PATH.exists():
        for line in LOG_PATH.read_text().strip().splitlines():
            try:
                t = json.loads(line)
            except Exception:
                continue
            if t.get("ts", "").startswith(today) and t.get("pnl") is not None:
                daily_pnl += float(t["pnl"])
    if daily_pnl <= -SCALP_DAILY_LOSS_LIMIT:
        return False, (
            f"daily loss limit hit: {daily_pnl:.2f} <= "
            f"-{SCALP_DAILY_LOSS_LIMIT:.2f}"
        )
    return True, f"daily P&L {daily_pnl:.2f} within limit"


def _latest_decision():
    """Read the latest multi-agent decision. Returns dict or None."""
    if LATEST_DECISION_PATH.exists():
        try:
            return json.loads(LATEST_DECISION_PATH.read_text())
        except Exception:
            return None
    # fallback: most recent file in decisions dir
    files = sorted(DECISIONS_PATH.glob("*.json"))
    if files:
        try:
            return json.loads(files[-1].read_text())
        except Exception:
            return None
    return None

def _veto_check(symbol, action):
    """Return (allowed, reason) based on deliberation. Fail-closed if no decision."""
    dec = _latest_decision()
    if not dec:
        return False, "no deliberation decision available - fail closed"
    pairs = dec.get("decision", {}).get("pairs")
    if not isinstance(pairs, dict):
        pairs = dec.get("pairs")
    if not isinstance(pairs, dict):
        pairs = {}
    item = pairs.get(symbol)
    if not item:
        return False, f"{symbol} not in deliberation - fail closed"
    d_action = item.get("action", "block")
    size = item.get("size", 0.0)
    if action in ("buy",) and d_action != "allow":
        return False, f"deliberation blocked {symbol}: {item.get('rationale','')}"
    if action in ("buy",) and (size is None or size <= 0):
        return False, f"deliberation size=0 for {symbol}"
    return True, f"deliberation allows {symbol} (size={size}, conf={item.get('confidence')})"


def _time_gate():
    """Block new entries if within 15 min of next 4-hour boundary.
    Returns (allowed, reason)."""
    now = datetime.now(timezone.utc)
    # next 4-hour boundary (00,04,08,12,16,20 UTC)
    hour = (now.hour // 4 + 1) * 4
    if hour >= 24:
        nxt = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        nxt = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    mins_left = (nxt - now).total_seconds() / 60.0
    if mins_left < 15:
        return False, f"only {mins_left:.0f} min to next 4h run - waiting for fresh decision"
    return True, f"{mins_left:.0f} min to next 4h run"

# ---------- paper broker ----------
def _load_state():
    if PAPER_STATE_PATH.exists():
        return json.loads(PAPER_STATE_PATH.read_text())
    return {"cash": 4.0, "positions": {}, "equity": 4.0, "trades": []}

def _save_state(s):
    PAPER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PAPER_STATE_PATH.write_text(json.dumps(s, indent=2, default=str))

def _log_trade(t):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(t, default=str) + "\n")

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.post("/webhook/tv")
async def tv_webhook(alert: TVAlert, x_tv_secret: str = Header(default="")):
    # validate secret
    if not (hmac.compare_digest(alert.secret, WEBHOOK_SECRET) or hmac.compare_digest(x_tv_secret, WEBHOOK_SECRET)):
        raise HTTPException(401, "bad secret")

    state = _load_state()
    ts = datetime.now(timezone.utc).isoformat()
    result = {"ts": ts, "alert": alert.model_dump(), "executed": False, "reason": ""}

    symbol = alert.symbol
    is_equity = _is_equity(alert)
    pos = state["positions"].get(symbol, {"qty": 0.0, "avg": 0.0})

    if alert.action == "buy":
        if is_equity:
            allowed, reason = _scalp_guard(state, alert)
            result["route"] = "scalp"
        else:
            allowed, reason = _veto_check(symbol, "buy")
            result["route"] = "deliberation"
        if not allowed:
            result["reason"] = reason
            _save_state(state)
            result["equity"] = state["equity"]
            result["cash"] = state["cash"]
            result["positions"] = state["positions"]
            return result
        t_allowed, t_reason = _time_gate()
        if not t_allowed:
            result["reason"] = t_reason
            _save_state(state)
            result["equity"] = state["equity"]
            result["cash"] = state["cash"]
            result["positions"] = state["positions"]
            return result
        # TradingView can override with an explicit qty (shares).
        if alert.qty is not None and alert.qty > 0:
            qty = float(alert.qty)
        else:
            stake = min(state["cash"] * 0.10, state["cash"])
            qty = stake / alert.price if alert.price > 0 else 0
        if qty <= 0:
            result["reason"] = "zero qty"
        else:
            cost = qty * alert.price
            state["cash"] -= cost
            new_qty = pos["qty"] + qty
            new_avg = (pos["qty"] * pos["avg"] + qty * alert.price) / new_qty if new_qty else alert.price
            state["positions"][symbol] = {"qty": new_qty, "avg": new_avg}
            trade = {"ts": ts, "symbol": symbol, "side": "buy", "qty": qty, "price": alert.price, "cost": cost}
            state["trades"].append(trade)
            _log_trade(trade)
            result["executed"] = True
            result["reason"] = f"bought {qty:.6f} @ {alert.price}"

    elif alert.action == "sell":
        if pos["qty"] <= 0:
            result["reason"] = "no position to sell"
        else:
            qty = pos["qty"]
            proceeds = qty * alert.price
            pnl = proceeds - (qty * pos["avg"])
            state["cash"] += proceeds
            state["positions"][symbol] = {"qty": 0.0, "avg": 0.0}
            trade = {"ts": ts, "symbol": symbol, "side": "sell", "qty": qty, "price": alert.price, "proceeds": proceeds, "pnl": pnl}
            state["trades"].append(trade)
            _log_trade(trade)
            result["executed"] = True
            result["reason"] = f"sold {qty:.6f} @ {alert.price} pnl={pnl:.2f}"

    elif alert.action == "close":
        if pos["qty"] > 0:
            qty = pos["qty"]
            proceeds = qty * alert.price
            pnl = proceeds - (qty * pos["avg"])
            state["cash"] += proceeds
            state["positions"][symbol] = {"qty": 0.0, "avg": 0.0}
            trade = {"ts": ts, "symbol": symbol, "side": "close", "qty": qty, "price": alert.price, "pnl": pnl}
            state["trades"].append(trade)
            _log_trade(trade)
            result["executed"] = True
            result["reason"] = f"closed {qty:.6f} pnl={pnl:.2f}"
        else:
            result["reason"] = "no position to close"

    # mark-to-market equity
    equity = state["cash"]
    for s, p in state["positions"].items():
        equity += p["qty"] * alert.price if s == symbol else 0
    state["equity"] = equity
    _save_state(state)
    result["equity"] = equity
    result["cash"] = state["cash"]
    result["positions"] = state["positions"]
    return result

@app.get("/portfolio")
def portfolio():
    state = _load_state()
    return state

@app.get("/trades")
def trades(limit: int = 50):
    if not LOG_PATH.exists():
        return []
    lines = LOG_PATH.read_text().strip().splitlines()
    return [json.loads(l) for l in lines[-limit:]]

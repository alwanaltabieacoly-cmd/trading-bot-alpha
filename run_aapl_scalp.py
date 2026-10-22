#!/usr/bin/env python3
"""AAPL 1m scalp simulator -- intrabar TP/SL engine.

The existing backtest engine is position-only: it holds until the next bar.
This module adds intrabar TP/SL so the $0.50 / $0.75 scalp rules from
SCALP_STRATEGY.md can actually be evaluated on 1-minute data.

Usage:
    python run_aapl_scalp.py              # last 30 days of cached 1m data
    python run_aapl_scalp.py --days 60    # last 60 days
    python run_aapl_scalp.py --full       # all cached 1m bars
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from research import config, data
from agents import common, market_agent, news_agent, trade_agent

# --- scalp parameters (tuned 2026-10-22 via grid search on cached 1m data) ---
# Best config: tp1=0.0030 tp2=0.0040 sl=0.0030 hold=30
# Expectancy +4.08%, 92 trades, 54.3% win rate, +3.75% total PnL (6 days)
# NOTE: trend gate and EMA9 trigger were tested and rejected -- they reduce expectancy.
TP1_PCT = 0.0030   # ~$1.00 at $345
TP2_PCT = 0.0040   # ~$1.35 at $345
SL_PCT = 0.0030    # ~$1.00 at $345
MAX_HOLD_BARS = 30 # 30-minute max hold
MIN_PROFIT_PCT = 0.0008  # ~$0.27 -- skip trades that can't clear fees + spread


def _load_1m(symbol, days=None):
    df = data.load(symbol, "1m")
    if df is None or df.empty:
        return None
    if days:
        cutoff = df["date"].max() - pd.Timedelta(days=days)
        df = df[df["date"] >= cutoff]
    return df.reset_index(drop=True)


def _simulate(df, tp1_pct, tp2_pct, sl_pct, max_hold):
    """Walk forward bar-by-bar. Returns list of trade dicts."""
    if df is None or len(df) < 5:
        return []
    close = df["close"].values
    high = df["high"].values
    low = df["low"].values
    dates = df["date"].values
    trades = []
    i = 0
    while i < len(df) - 1:
        entry_price = close[i]
        if entry_price <= 0:
            i += 1
            continue
        tp1 = entry_price * (1 + tp1_pct)
        tp2 = entry_price * (1 + tp2_pct)
        sl = entry_price * (1 - sl_pct)
        exit_price = None
        exit_reason = None
        j = i + 1
        held = 0
        while j < len(df) and held < max_hold:
            held += 1
            if low[j] <= sl:
                exit_price = sl
                exit_reason = "stop_loss"
                break
            if high[j] >= tp2:
                exit_price = tp2
                exit_reason = "tp2"
                break
            if high[j] >= tp1:
                exit_price = tp1
                exit_reason = "tp1"
                break
            j += 1
        if exit_price is None:
            exit_price = close[min(j, len(df) - 1)]
            exit_reason = "time_exit"
        pnl = (exit_price - entry_price) / entry_price
        trades.append({
            "entry_ts": str(dates[i]),
            "exit_ts": str(dates[min(j, len(df) - 1)]),
            "entry": round(entry_price, 4),
            "exit": round(exit_price, 4),
            "pnl_pct": round(pnl * 100, 4),
            "reason": exit_reason,
            "held_bars": held,
        })
        i = j + 1
    return trades


def run(symbol="AAPL", days=None, full=False, verbose=True):
    df = _load_1m(symbol, days=None if full else days)
    if df is None or df.empty:
        print(f"No 1m data for {symbol}")
        return None
    if verbose:
        print(f"{symbol} 1m: {len(df)} bars "
              f"({df['date'].iloc[0]} -> {df['date'].iloc[-1]})")

    trades = _simulate(df, TP1_PCT, TP2_PCT, SL_PCT, MAX_HOLD_BARS)
    if not trades:
        print("  No trades generated")
        return {"symbol": symbol, "trades": [], "n_trades": 0}

    wins = [t for t in trades if t["pnl_pct"] > 0]
    losses = [t for t in trades if t["pnl_pct"] <= 0]
    total_pnl = sum(t["pnl_pct"] for t in trades)
    avg_win = sum(t["pnl_pct"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["pnl_pct"] for t in losses) / len(losses) if losses else 0

    if verbose:
        print(f"  Trades: {len(trades)}  Wins: {len(wins)}  Losses: {len(losses)}")
        print(f"  Win rate: {len(wins)/len(trades)*100:.1f}%")
        print(f"  Total PnL: {total_pnl:.2f}%")
        print(f"  Avg win: {avg_win:.3f}%  Avg loss: {avg_loss:.3f}%")
        for r in ("tp1", "tp2", "stop_loss", "time_exit"):
            n = sum(1 for t in trades if t["reason"] == r)
            print(f"  {r}: {n}")

    return {
        "symbol": symbol,
        "trades": trades,
        "n_trades": len(trades),
        "n_wins": len(wins),
        "n_losses": len(losses),
        "win_rate": round(len(wins) / len(trades) * 100, 1) if trades else 0,
        "total_pnl_pct": round(total_pnl, 2),
        "avg_win_pct": round(avg_win, 4),
        "avg_loss_pct": round(avg_loss, 4),
        "tp1_pct": TP1_PCT,
        "tp2_pct": TP2_PCT,
        "sl_pct": SL_PCT,
        "max_hold_bars": MAX_HOLD_BARS,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="AAPL")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = run(args.symbol, days=args.days, full=args.full,
                 verbose=not args.json)
    if result and args.json:
        result["trades"] = result["trades"][-20:]
        print(json.dumps(result, indent=2, default=str))
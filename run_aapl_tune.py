#!/usr/bin/env python3
"""Grid-search AAPL 1m scalp parameters to find positive expectancy.

Tests combinations of TP1, TP2, SL, max_hold, trend_gate, ema_trigger.
Reports the best configuration by net expectancy (win_pct * avg_win - loss_pct * avg_loss).
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from research import data


def _load_1m(symbol, days=None):
    df = data.load(symbol, "1m")
    if df is None or df.empty:
        return None
    if days:
        cutoff = df["date"].max() - pd.Timedelta(days=days)
        df = df[df["date"] >= cutoff]
    return df.reset_index(drop=True)


def _ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def _simulate(df, tp1, tp2, sl, max_hold, trend_gate, ema_trigger):
    """Walk forward bar-by-bar with optional trend gate and EMA9 trigger."""
    if df is None or len(df) < 10:
        return []
    close = df["close"].values
    high = df["high"].values
    low = df["low"].values
    dates = df["date"].values

    ema9 = _ema(df["close"], 9).values
    ema21 = _ema(df["close"], 21).values

    trades = []
    i = 0
    while i < len(df) - 1:
        entry_price = close[i]
        if entry_price <= 0:
            i += 1
            continue

        # Trend gate: only long if price > EMA21
        if trend_gate and i >= 21:
            if entry_price <= ema21[i]:
                i += 1
                continue

        # EMA9 trigger: only enter if EMA9 is rising
        if ema_trigger and i >= 10:
            if ema9[i] <= ema9[i - 1]:
                i += 1
                continue

        tp1_p = entry_price * (1 + tp1)
        tp2_p = entry_price * (1 + tp2)
        sl_p = entry_price * (1 - sl)
        exit_price = None
        exit_reason = None
        j = i + 1
        held = 0
        while j < len(df) and held < max_hold:
            held += 1
            if low[j] <= sl_p:
                exit_price = sl_p
                exit_reason = "stop_loss"
                break
            if high[j] >= tp2_p:
                exit_price = tp2_p
                exit_reason = "tp2"
                break
            if high[j] >= tp1_p:
                exit_price = tp1_p
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


def _evaluate(trades, tp1, tp2, sl, max_hold, trend_gate, ema_trigger):
    if not trades:
        return None
    wins = [t for t in trades if t["pnl_pct"] > 0]
    losses = [t for t in trades if t["pnl_pct"] <= 0]
    n = len(trades)
    win_rate = len(wins) / n * 100
    avg_win = sum(t["pnl_pct"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["pnl_pct"] for t in losses) / len(losses) if losses else 0
    total_pnl = sum(t["pnl_pct"] for t in trades)
    expectancy = (win_rate / 100) * avg_win - ((100 - win_rate) / 100) * (-avg_loss)
    return {
        "tp1": tp1, "tp2": tp2, "sl": sl, "max_hold": max_hold,
        "trend_gate": trend_gate, "ema_trigger": ema_trigger,
        "n_trades": n, "n_wins": len(wins), "n_losses": len(losses),
        "win_rate": round(win_rate, 1),
        "avg_win": round(avg_win, 4),
        "avg_loss": round(avg_loss, 4),
        "total_pnl_pct": round(total_pnl, 2),
        "expectancy": round(expectancy, 6),
    }


def run(symbol="AAPL", days=30, top_n=10):
    df = _load_1m(symbol, days=days)
    if df is None or df.empty:
        print(f"No 1m data for {symbol}")
        return None
    print(f"{symbol} 1m: {len(df)} bars ({df['date'].iloc[0]} -> {df['date'].iloc[-1]})")

    tp1_vals = [0.0015, 0.0020, 0.0025, 0.0030, 0.0040, 0.0050]
    tp2_vals = [0.0030, 0.0040, 0.0050, 0.0060, 0.0080]
    sl_vals = [0.0015, 0.0022, 0.0030, 0.0045]
    hold_vals = [5, 10, 15, 20, 30]
    gates = [(False, False), (True, False), (True, True)]

    results = []
    total = len(tp1_vals) * len(tp2_vals) * len(sl_vals) * len(hold_vals) * len(gates)
    count = 0
    for tp1, tp2, sl, hold, (tg, et) in itertools.product(
        tp1_vals, tp2_vals, sl_vals, hold_vals, gates
    ):
        count += 1
        if count % 50 == 0:
            print(f"  ... {count}/{total}")
        trades = _simulate(df, tp1, tp2, sl, hold, tg, et)
        r = _evaluate(trades, tp1, tp2, sl, hold, tg, et)
        if r:
            results.append(r)

    results.sort(key=lambda r: r["expectancy"], reverse=True)
    print(f"\n=== TOP {top_n} CONFIGURATIONS (by expectancy) ===")
    for i, r in enumerate(results[:top_n]):
        print(f"#{i+1} exp={r['expectancy']:.5f} "
              f"tp1={r['tp1']:.4f} tp2={r['tp2']:.4f} sl={r['sl']:.4f} "
              f"hold={r['max_hold']} trend={r['trend_gate']} ema={r['ema_trigger']} "
              f"trades={r['n_trades']} win={r['win_rate']}% "
              f"pnl={r['total_pnl_pct']:+.2f}%")

    return results


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="AAPL")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    results = run(args.symbol, days=args.days, top_n=args.top)
    if results and args.json:
        print(json.dumps(results[:args.top], indent=2, default=str))

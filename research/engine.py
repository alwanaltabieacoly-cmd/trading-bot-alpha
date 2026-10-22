"""Backtest engine with real costs and no look-ahead.

The signal for bar t is computed from data up to and including bar t, and
the position is only taken from bar t+1. Fees and slippage are charged on
every change of position - entry and exit both pay.

No future data can reach the signal, and the only way to trade on bar t
is to have decided on bar t-1.
"""
import numpy as np
import pandas as pd

from . import config


def to_position(signal):
    """Boolean signal -> 0/1 position with a one bar lag."""
    sig = np.asarray(signal, dtype=bool)
    pos = np.zeros(len(sig), dtype=float)
    pos[1:] = sig[:-1].astype(float)
    return pos


def backtest(df, signal, cost_per_side=None):
    """Return (per-bar returns, position, trades)."""
    if cost_per_side is None:
        cost_per_side = config.COST_PER_SIDE
    close = df["close"].to_numpy(dtype="float64")
    n = len(close)
    if n < 3:
        return np.zeros(n), np.zeros(n), 0

    pos = to_position(signal)
    price_ret = np.zeros(n)
    price_ret[1:] = close[1:] / close[:-1] - 1.0

    turnover = np.zeros(n)
    turnover[1:] = np.abs(pos[1:] - pos[:-1])

    net = pos * price_ret - turnover * cost_per_side
    trades = int(np.count_nonzero(turnover > 0))
    return net, pos, trades


def buy_and_hold(df, cost_per_side=None):
    if cost_per_side is None:
        cost_per_side = config.COST_PER_SIDE
    close = df["close"].to_numpy(dtype="float64")
    n = len(close)
    pos = np.zeros(n)
    pos[1:] = 1.0
    price_ret = np.zeros(n)
    price_ret[1:] = close[1:] / close[:-1] - 1.0
    turnover = np.zeros(n)
    turnover[1:] = np.abs(pos[1:] - pos[:-1])
    return pos * price_ret - turnover * cost_per_side, 1


def metrics(returns, periods_per_year):
    """Performance metrics from a per-bar return series."""
    returns = np.asarray(returns, dtype="float64")
    if len(returns) < 3:
        return {}
    equity = np.cumprod(1.0 + returns)
    total = equity[-1] - 1.0
    years = len(returns) / periods_per_year
    if years <= 0:
        return {}

    cagr = (equity[-1] ** (1.0 / years) - 1.0) if equity[-1] > 0 else -1.0
    peak = np.maximum.accumulate(equity)
    dd = (equity - peak) / peak
    max_dd = dd.min()

    sd = returns.std(ddof=1)
    sharpe = (returns.mean() / sd) * np.sqrt(periods_per_year) if sd > 0 else float("nan")
    downside = returns[returns < 0]
    dsd = downside.std(ddof=1) if len(downside) > 1 else float("nan")
    sortino = (returns.mean() / dsd) * np.sqrt(periods_per_year) if dsd and dsd > 0 else float("nan")
    calmar = (cagr / abs(max_dd)) if max_dd < 0 else float("nan")
    downside_dev = (np.sqrt(np.mean(np.minimum(returns, 0) ** 2))
                    if len(returns) else float("nan"))

    return {
        "total_return_pct": round(total * 100, 2),
        "cagr_pct": round(cagr * 100, 2),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "sharpe": round(float(sharpe), 3),
        "sortino": round(float(sortino), 3),
        "calmar": round(float(calmar), 3),
        "final_equity": round(float(equity[-1]), 4),
        "bars": int(len(returns)),
        "years": round(years, 3),
    }


def evaluate(df, signal, timeframe, mask=None, symbol=None):
    """Backtest a signal over an optional boolean mask of bars."""
    cost = config.cost_per_side(symbol) if symbol else config.COST_PER_SIDE
    net, pos, trades = backtest(df, signal, cost_per_side=cost)
    bh, bh_trades = buy_and_hold(df, cost_per_side=cost)
    ppy = config.periods_per_year(symbol, timeframe) if symbol else config.PERIODS_PER_YEAR[timeframe]
    m = metrics(net if mask is None else net[mask], ppy)
    b = metrics(bh if mask is None else bh[mask], ppy)
    m["trades"] = trades
    m["exposure_pct"] = round(
        float(np.mean(pos if mask is None else pos[mask])) * 100, 2
    )
    m["buy_hold"] = {
        "total_return_pct": b.get("total_return_pct"),
        "cagr_pct": b.get("cagr_pct"),
        "max_drawdown_pct": b.get("max_drawdown_pct"),
        "sharpe": b.get("sharpe"),
    }
    return m


def date_mask(dates, start=None, end=None):
    """Boolean mask selecting bars within [start, end)."""
    s = pd.to_datetime(dates, utc=True)
    mask = np.ones(len(s), dtype=bool)
    if start:
        cmp = s >= pd.Timestamp(start, tz="UTC")
        mask &= np.asarray(cmp, dtype=bool).reshape(-1)
    if end:
        cmp = s < pd.Timestamp(end, tz="UTC")
        mask &= np.asarray(cmp, dtype=bool).reshape(-1)
    return np.asarray(mask, dtype=bool)

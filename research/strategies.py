"""Strategy registry.

Every strategy is a named, parameterised rule that maps OHLCV to a
long/cash position. The point of keeping the search space small and
explicit is that a small, readable space cannot hide a curve-fit.

Each entry is:  name -> (build_params, signal_function)
where signal_function(df, **params) returns a boolean Series (True = hold).
"""
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _sma(s, n):
    return s.rolling(n).mean()


def _ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def _rsi(s, n=14):
    delta = s.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(df, n=14):
    high, low, prev_close = df["high"], df["low"], df["close"].shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.rolling(n).mean()


# --------------------------------------------------------------------------
# strategies
# --------------------------------------------------------------------------


def sma_trend(df, period=200):
    """Hold while close is above its n-period SMA. The proven baseline."""
    ma = _sma(df["close"], period)
    return (df["close"] > ma).fillna(False)


def ema_trend(df, fast=50, slow=200):
    """Hold while the fast EMA is above the slow EMA."""
    return (_ema(df["close"], fast) > _ema(df["close"], slow)).fillna(False)


def donchian_trend(df, period=100):
    """Hold while close is at the n-bar high (breakout trend following)."""
    prior_high = df["high"].rolling(period).max().shift(1)
    return (df["close"] >= prior_high).fillna(False)


def sma_trend_vol_filter(df, period=200, vol_lookback=30, vol_max_pct=3.0):
    """Trend filter, but stand aside when recent volatility is extreme.

    Crypto's biggest crashes come with a volatility spike. Sitting out of
    those is where a large part of the trend rule's edge comes from.
    """
    trend = sma_trend(df, period)
    atr_pct = (_atr(df, 30) / df["close"] * 100.0)
    vol_ok = atr_pct < vol_max_pct
    return (trend & vol_ok).fillna(False)


def sma_trend_rsi_filter(df, period=200, rsi_period=14, rsi_max=70):
    """Trend filter plus an overbought guard."""
    trend = sma_trend(df, period)
    not_overbought = _rsi(df["close"], rsi_period) < rsi_max
    return (trend & not_overbought).fillna(False)


def sma_trend_fast_slow(df, slow_period=200, fast_period=20):
    """Trend filter confirmed by a short-term pullback recovery.

    Enter on a pullback that turns back up, but only inside a long-term
    uptrend. The intent is to enter with less slippage risk than buying
    the exact top.
    """
    slow = _sma(df["close"], slow_period)
    fast = _sma(df["close"], fast_period)
    trend = df["close"] > slow
    recovering = fast > fast.shift(1)
    return (trend & recovering).fillna(False)


def ema_trend_regime(df, fast=50, slow=200, atr_period=14, atr_max_pct=4.0):
    """EMA cross, but only when volatility is not extreme."""
    trend = _ema(df["close"], fast) > _ema(df["close"], slow)
    atr_pct = (_atr(df, atr_period) / df["close"] * 100.0)
    return (trend & (atr_pct < atr_max_pct)).fillna(False)


def donchian_trend_vol_filter(df, period=100, atr_period=14, atr_max_pct=4.0):
    """Breakout trend with a volatility guard."""
    prior_high = df["high"].rolling(period).max().shift(1)
    trend = df["close"] >= prior_high
    atr_pct = (_atr(df, atr_period) / df["close"] * 100.0)
    return (trend & (atr_pct < atr_max_pct)).fillna(False)


def sma_trend_slope(df, period=200, slope_bars=20):
    """Hold while close is above its SMA AND the SMA itself is rising.

    Requiring the long-term average to be rising rejects the case where
    price sits just above a flattening average - the market that chops
    around a trend and eats fees.
    """
    ma = _sma(df["close"], period)
    s = (df["close"] > ma) & (ma > ma.shift(slope_bars))
    return np.where(np.isnan(s), False, s)


def sma_trend_confirm(df, slow_period=200, fast_period=50):
    """Hold while close is above the slow SMA AND the fast SMA is above it.

    A slower confirmation than a golden cross: the fast average has to be
    above the slow one, so the bot buys a trend that has already started
    rather than the first touch of the average.
    """
    slow = _sma(df["close"], slow_period)
    fast = _sma(df["close"], fast_period)
    s = (df["close"] > slow) & (fast > slow)
    return np.where(np.isnan(s), False, s)


def sma_trend_efficiency(df, period=200, er_n=30, er_min=0.25):
    """Hold while close is above its SMA AND the market is trending cleanly.

    Kaufman's efficiency ratio is net movement divided by total movement.
    A ratio near 1 means price went straight one way; near 0 means it
    thrashed. This is a different lens from volatility: a market can be
    quiet but directionless, or volatile but cleanly trending.
    """
    ma = _sma(df["close"], period)
    net = (df["close"] - df["close"].shift(er_n)).abs()
    path = df["close"].diff().abs().rolling(er_n).sum()
    er = net / path.replace(0, np.nan)
    s = (df["close"] > ma) & (er > er_min)
    return np.where(np.isnan(s), False, s)


# --- equity scalp strategies (TradingView integration) --------------------
def aapl_scalp_trend(df, sma_period=200, ema_period=9, rsi_period=14, rsi_max=50):
    """1-min AAPL scalp: enter long when price > SMA200 (uptrend),
    RSI < 50 (not overbought), and EMA9 is turning up (bounce).
    This is the bar-level approximation of the TradingView scalp rules
    in SCALP_STRATEGY.md. The intrabar TP/SL ($0.50/$0.75) cannot be
    modelled in a position-only backtest, so the edge here is the trend
    filter + pullback entry, which is what actually decides whether to
    be in the market at all.
    """
    close = df["close"]
    sma = _sma(close, sma_period)
    ema = _ema(close, ema_period)
    rsi = _rsi(close, rsi_period)

    uptrend = close > sma
    not_overbought = rsi < rsi_max
    ema_rising = ema > ema.shift(1)

    entry = uptrend & not_overbought & ema_rising
    return entry.fillna(False)


def aapl_scalp_reversion(df, ema_period=9, rsi_oversold=30, rsi_overbought=70):
    """Mean-reversion scalp: enter when RSI dips below oversold and
    price bounces off EMA9. Exit when RSI reaches overbought.
    Works on the 1m AAPL chart where mean reversion dominates
    over trend-following inside the day.
    """
    close = df["close"]
    ema = _ema(close, ema_period)
    rsi = _rsi(close, 14)

    oversold = rsi < rsi_oversold
    ema_rising = ema > ema.shift(1)
    entry = oversold & ema_rising

    overbought = rsi > rsi_overbought
    exit_sig = overbought & (ema < ema.shift(1))

    pos = entry.copy()
    pos[exit_sig] = False
    return pos.fillna(False).astype(bool)


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
# Each tuple: (id, description, {param: [values]}, signal_fn)
# The runner expands every id x every parameter combination into a candidate.

REGISTRY = [
    (
        "sma_trend",
        "close > SMA(n), else cash",
        {"period": [50, 100, 125, 150, 175, 200, 225, 250, 275, 300, 400]},
        sma_trend,
    ),
    (
        "ema_trend",
        "EMA(fast) > EMA(slow)",
        {"fast": [20, 50], "slow": [100, 200, 300]},
        ema_trend,
    ),
    (
        "donchian_trend",
        "close at n-bar high",
        {"period": [50, 100, 200]},
        donchian_trend,
    ),
    (
        "sma_trend_vol_filter",
        "close > SMA(n) and ATR% below limit",
        {
            "period": [100, 150, 175, 200, 225, 250, 300],
            "vol_lookback": [30],
            "vol_max_pct": [1.5, 2.0, 2.5, 3.0, 4.0],
        },
        sma_trend_vol_filter,
    ),
    (
        "sma_trend_rsi_filter",
        "close > SMA(n) and RSI below limit",
        {
            "period": [100, 150, 200, 250],
            "rsi_period": [14],
            "rsi_max": [60, 70, 80],
        },
        sma_trend_rsi_filter,
    ),
    (
        "sma_trend_fast_slow",
        "close > SMA(slow) and fast SMA rising",
        {"slow_period": [100, 150, 200, 250], "fast_period": [10, 20, 50]},
        sma_trend_fast_slow,
    ),
    (
        "ema_trend_regime",
        "EMA cross with volatility guard",
        {
            "fast": [20, 50],
            "slow": [100, 200],
            "atr_period": [14],
            "atr_max_pct": [2.0, 3.0, 4.0],
        },
        ema_trend_regime,
    ),
    (
        "donchian_trend_vol_filter",
        "breakout trend with volatility guard",
        {
            "period": [50, 100, 200],
            "atr_period": [14],
            "atr_max_pct": [2.0, 3.0, 4.0],
        },
        donchian_trend_vol_filter,
    ),
    # --- newer ideas, added because the evidence pointed at the trend
    # --- families being the strongest. These are new CONDITIONS, not
    # --- finer versions of an existing grid.
    (
        "sma_trend_slope",
        "close > SMA(n) and the SMA is rising",
        {"period": [100, 150, 200, 250], "slope_bars": [10, 20, 40]},
        sma_trend_slope,
    ),
    (
        "sma_trend_confirm",
        "close > SMA(slow) and SMA(fast) above SMA(slow)",
        {"slow_period": [100, 150, 200, 250], "fast_period": [20, 50]},
        sma_trend_confirm,
    ),
    (
        "sma_trend_efficiency",
        "close > SMA(n) and efficiency ratio above a floor",
        {
            "period": [100, 150, 200, 250],
            "er_n": [20, 30],
            "er_min": [0.2, 0.3],
        },
        sma_trend_efficiency,
    ),
    # --- equity scalp families (TradingView integration) -------------------
    # These are the bar-level approximation of the AAPL 1m scalp rules.
    # The intrabar TP/SL cannot be modelled in a position-only backtest,
    # so the edge tested here is the trend filter + entry logic, which is
    # what actually decides whether to be in the market at all.
    (
        "aapl_scalp_trend",
        "1m AAPL: close > SMA200 + RSI < 50 + EMA9 rising",
        {
            "sma_period": [200],
            "ema_period": [9, 21],
            "rsi_period": [14],
            "rsi_max": [45, 50, 55],
        },
        aapl_scalp_trend,
    ),
    (
        "aapl_scalp_reversion",
        "1m AAPL: RSI oversold + EMA9 bounce, exit on overbought",
        {
            "ema_period": [9, 21],
            "rsi_oversold": [25, 30, 35],
            "rsi_overbought": [65, 70, 75],
        },
        aapl_scalp_reversion,
    ),
]


def retired_families():
    """Families the evolution step has retired based on accumulated evidence.

    A retired family is one whose every variant lost money on the untouched
    window across several separated runs. Removing it stops the harness
    burning trials on a rule that is known to be harmful.
    """
    import json
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "research", "evolution.json")
    if not os.path.exists(path):
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("retired_families", []) or [])
    except Exception:
        return set()


def champion_anchor():
    """The champion's own parameter set, so it is always still evaluable.

    Retirement must never delete the strategy we are currently using -
    otherwise we could no longer measure whether the current champion still
    wins.
    """
    import json
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "research", "state", "champion.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        champ = state.get("champion") or {}
        return champ.get("id"), champ.get("params") or {}
    except Exception:
        return None


def expand():
    """Yield (candidate_id, params, fn, family, desc) for every combination."""
    import itertools

    retired = retired_families()
    anchor = champion_anchor()

    out = []
    for sid, desc, grid, fn in REGISTRY:
        if sid in retired:
            continue
        keys = list(grid.keys())
        for combo in itertools.product(*[grid[k] for k in keys]):
            params = dict(zip(keys, combo))
            cid = sid + "_" + "_".join(f"{k}{v}" for k, v in params.items())
            out.append((cid, params, fn, sid, desc))

    # Guarantee the champion is always in the space, even if its family was
    # retired or its parameters drifted outside the current grid.
    if anchor:
        anchor_id, anchor_params = anchor
        if anchor_id and not any(c[0] == anchor_id for c in out):
            for sid, desc, grid, fn in REGISTRY:
                if anchor_id.startswith(sid + "_"):
                    out.append((anchor_id, anchor_params, fn, sid, desc))
                    break

    return out


def describe(cid, params):
    return cid + " " + ",".join(f"{k}={v}" for k, v in sorted(params.items()))

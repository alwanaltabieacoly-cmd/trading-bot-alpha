"""Market data fetching and caching.

Uses the public Bybit API through ccxt - no API key needed for candles.
Data is cached as parquet under research/data/ and committed to the repo so
every daily run is auditable and reproducible.
"""
import os
import time

import pandas as pd

from . import config

PARQUET_ENGINE = "pyarrow"


def _cache_path(asset, timeframe):
    return os.path.join(config.DATA_DIR, f"{asset}_{timeframe}.parquet")


def fetch_candles(asset, timeframe, days_back=1600, retries=3):
    """Fetch OHLCV from Bybit public API."""
    import ccxt

    ex = ccxt.bybit({"enableRateLimit": True})
    since = ex.parse8601(
        f"{(pd.Timestamp.utcnow() - pd.Timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')}"
    )
    all_rows = []
    while since < ex.milliseconds():
        try:
            rows = ex.fetch_ohlcv(
                f"{asset}/USDT", timeframe=timeframe, since=since, limit=1000
            )
        except Exception as e:
            if retries <= 0:
                raise
            retries -= 1
            time.sleep(5)
            continue
        if not rows:
            break
        all_rows.extend(rows)
        last = rows[-1][0]
        if last <= since:
            break
        since = last + 1
        time.sleep(ex.rateLimit / 1000)

    df = pd.DataFrame(
        all_rows, columns=["ts", "open", "high", "low", "close", "volume"]
    )
    df["date"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.drop(columns=["ts"]).drop_duplicates(subset=["date"]).sort_values("date")
    return df.reset_index(drop=True)


def fetch_equity_candles(symbol, timeframe, days_back=800, retries=3):
    """Fetch OHLCV from Yahoo Finance (free, no API key).
    Used for the equity assets (AAPL) that are not on Bybit.
    """
    import yfinance as yf

    tf_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "1d": "1d"}
    ytf = tf_map.get(timeframe, "1d")

    end = pd.Timestamp.utcnow()
    start = end - pd.Timedelta(days=days_back)
    if timeframe == "1m":
        # Yahoo only serves 1m for the last 7 days via the API
        start = end - pd.Timedelta(days=7)

    df = yf.download(
        symbol, interval=ytf, start=start, end=end,
        auto_adjust=False, progress=False, timeout=30,
    )
    if df is None or len(df) == 0:
        return None

    # yfinance returns a MultiIndex (field, ticker) for single symbols too.
    # Flatten it and lowercase everything so the column names are stable.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower() for c in df.columns]

    df = df.reset_index()
    # The date column may be named "Date" or "Datetime"
    date_col = None
    for cand in ("date", "datetime", "index"):
        if cand in df.columns:
            date_col = cand
            break
    if date_col is None:
        date_col = df.columns[0]
    df = df.rename(columns={date_col: "date"})

    keep = [c for c in ["date", "open", "high", "low", "close", "volume"] if c in df.columns]
    df = df[keep].copy()
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.dropna(subset=["close"]).drop_duplicates(subset=["date"]).sort_values("date")
    return df.reset_index(drop=True)


def update_asset(asset, timeframe, days_back=1600):
    """Fetch and merge into the local cache. Returns the cached frame."""
    path = _cache_path(asset, timeframe)
    if asset in config.EQUITY_ASSETS:
        new = fetch_equity_candles(asset, timeframe, days_back=days_back)
    else:
        new = fetch_candles(asset, timeframe, days_back=days_back)

    if new is None or len(new) == 0:
        print(f"  WARNING: no data fetched for {asset} {timeframe}")
        return None

    if os.path.exists(path):
        try:
            old = pd.read_parquet(path)
        except Exception:
            old = None
        if old is not None and len(old):
            new = (
                pd.concat([old, new], ignore_index=True)
                .drop_duplicates(subset=["date"], keep="last")
                .sort_values("date")
                .reset_index(drop=True)
            )

    new.to_parquet(path, index=False, engine=PARQUET_ENGINE)
    return new


def load(asset, timeframe):
    """Load cached data. Returns None if not cached yet."""
    path = _cache_path(asset, timeframe)
    if not os.path.exists(path):
        return None
    try:
        return pd.read_parquet(path)
    except Exception:
        return None


def update_all(assets=None, timeframes=None, days_back=1600):
    assets = assets or config.ASSETS
    timeframes = timeframes or config.TIMEFRAMES
    result = {}
    for a in assets:
        for tf in timeframes:
            # Yahoo Finance caps intraday history:
            #   1m: 7 days, 5m/15m: 60 days, 1h: 730 days, 1d: unlimited
            cap = {"1m": 6, "5m": 55, "15m": 55, "1h": 700}.get(tf, 1600)
            try:
                df = update_asset(a, tf, days_back=min(days_back, cap))
                result[(a, tf)] = df
                if df is not None:
                    print(f"  {a} {tf}: {len(df)} bars "
                          f"({df['date'].iloc[0]} -> {df['date'].iloc[-1]})", flush=True)
                else:
                    print(f"  {a} {tf}: no data", flush=True)
            except Exception as e:
                print(f"  {a} {tf}: FAILED {type(e).__name__}: {e}", flush=True)
    return result

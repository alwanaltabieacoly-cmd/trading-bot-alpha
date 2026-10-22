#!/usr/bin/env python3
"""Fetch live candles from Bybit and update the parquet cache.

Used by the GitHub Actions warmup workflow so the Trade Agent reads
fresh market data, not stale committed cache.

The regime signal (bull/bear/range) depends on this -- without it,
the warmup verdict is computed from days-old prices.

Usage:
    python fetch_live.py                    # default pairs + timeframes
    python fetch_live.py --pairs BTC ETH     # specific base symbols
    python fetch_live.py --tf 1h 4h 1d       # specific timeframes
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from research import config, data

# Timeframes worth fetching live before the warmup.  We don't need 1m
# (Yahoo/Bybit limits + the scalp runs locally on cached 1m).
WARMUP_TFS = ["1h", "4h", "1d"]


def fetch_one(asset, tf):
    """Fetch the latest bars for asset/tf and merge into the parquet cache."""
    try:
        import ccxt
    except ImportError:
        print(f"  {asset} {tf}: ccxt not installed")
        return None

    ex = ccxt.bybit({"enableRateLimit": True})
    try:
        # Fetch the last ~200 bars -- enough for EMA50/EMA200 + regime.
        since = ex.parse8601(
            (pd.Timestamp.utcnow() - pd.Timedelta(hours=48)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        )
        rows = []
        remaining = True
        while remaining and len(rows) < 500:
            try:
                batch = ex.fetch_ohlcv(
                    f"{asset}/USDT", timeframe=tf, since=since, limit=200
                )
            except Exception as exc:
                print(f"  {asset} {tf}: fetch error {exc}")
                break
            if not batch:
                remaining = False
                break
            rows.extend(batch)
            last = batch[-1][0]
            if last <= since:
                break
            since = last + 1
            time.sleep(ex.rateLimit / 1000)
    except Exception as exc:
        print(f"  {asset} {tf}: ERROR {type(exc).__name__}: {exc}")
        return None

    if not rows:
        print(f"  {asset} {tf}: no rows returned")
        return None

    new = pd.DataFrame(
        rows, columns=["ts", "open", "high", "low", "close", "volume"]
    )
    new["date"] = pd.to_datetime(new["ts"], unit="ms", utc=True)
    new = new.drop(columns=["ts"]).drop_duplicates(subset=["date"]).sort_values("date")

    # Merge with existing cache so we don't lose history.
    path = data._cache_path(asset, tf)
    if os.path.exists(path):
        try:
            old = pd.read_parquet(path)
            merged = (
                pd.concat([old, new], ignore_index=True)
                .drop_duplicates(subset=["date"], keep="last")
                .sort_values("date")
                .reset_index(drop=True)
            )
        except Exception:
            merged = new.reset_index(drop=True)
    else:
        merged = new.reset_index(drop=True)

    try:
        merged.to_parquet(path, index=False, engine=data.PARQUET_ENGINE)
    except Exception as exc:
        print(f"  {asset} {tf}: write error {exc}")
        return None

    print(
        f"  {asset} {tf}: {len(new)} new bars, "
        f"cache now {len(merged)} "
        f"({merged['date'].iloc[0]} -> {merged['date'].iloc[-1]})"
    )
    return merged


def run(pairs=None, timeframes=None):
    pairs = pairs or config.ASSETS
    timeframes = timeframes or WARMUP_TFS
    print(f"Fetching live candles for {pairs} on {timeframes}")
    results = {}
    for asset in pairs:
        for tf in timeframes:
            results[(asset, tf)] = fetch_one(asset, tf)
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", default=None)
    ap.add_argument("--tf", nargs="+", default=None)
    args = ap.parse_args()
    run(pairs=args.pairs, timeframes=args.tf)
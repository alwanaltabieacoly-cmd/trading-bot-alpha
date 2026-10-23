#!/usr/bin/env python3
"""Scan crypto pairs and rank them by warmup score + profitability.

Universe rule: the scanner ranks the majors we actually maintain data for
(``research.config.ASSETS`` intersected with the curated list below), so a run
is deterministic and never depends on a live exchange listing. The Kraken
market list is only used to drop pairs that are no longer tradable.

Why this changed: the old version took the alphabetical first 20 Kraken USD
bases (1INCH, AAVE, ADA, ...), which have no local parquet cache, and dropped
every one silently -- so ``research/reports/asset_scan.json`` was permanently
``[]``. Skips are now reported on stderr with a reason.

Usage:
    python asset_scanner.py                    # scan, human table
    python asset_scanner.py --top 10           # show top 10
    python asset_scanner.py --json             # stdout = pure JSON (logs -> stderr)
    python asset_scanner.py --tf 1h            # different timeframe (default 4h)
    python asset_scanner.py --fetch-missing    # download missing pairs (slow; writes cache)
    python asset_scanner.py --strict           # exit 1 if nothing could be scored
"""
import argparse
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import common, feature_engine
from research import config

# Untracked cache for pairs outside config.ASSETS (git-ignored): keeps the
# scanner able to rank a wide universe without bloating the repository.
SCAN_CACHE_DIR = os.path.join(config.DATA_DIR, "scan")

# Curated universe, in priority order. Only bases that exist in the local
# research cache can be scored; the rest are reported as skips.
DEFAULT_PAIRS = [
    "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "LINK",
    "DOT", "MATIC", "LTC", "BCH", "UNI", "ATOM", "XLM", "NEAR", "ALGO",
    "FIL", "ICP", "APT", "ARB", "OP", "SAND", "MANA", "SHIB", "PEPE",
    "INJ", "TIA", "JTO", "GALA", "AXS",
]

MIN_BARS = 20
FETCH_DAYS = {"1m": 7, "5m": 60, "15m": 60, "1h": 120, "4h": 365, "1d": 1200}


def _log(msg="", as_json=False):
    """Human/progress output.

    In --json mode it goes to stderr so stdout stays parseable JSON: the warmup
    workflow redirects stdout straight into research/reports/asset_scan.json,
    and mixing log lines into that file corrupted it (preflight caught it).
    """
    print(msg, file=sys.stderr if as_json else sys.stdout)


def _cached_bases(tf):
    """Bases that actually have a research parquet cache for this timeframe."""
    out = []
    for base in config.ASSETS:
        path = os.path.join(config.DATA_DIR, f"{base}_{tf}.parquet")
        if os.path.exists(path):
            out.append(base)
    return out


def _scan_cache_path(base, tf):
    return os.path.join(SCAN_CACHE_DIR, f"{base}_{tf}.parquet")


def _load_scan_cache(base, tf):
    """Load a scan-only cached frame (untracked), or None."""
    path = _scan_cache_path(base, tf)
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_parquet(path)
    except Exception:
        return None
    if df is None or len(df) == 0 or "date" not in df.columns:
        return None
    return df


def _fetch_scan_cache(base, tf, days):
    """Download a pair into the untracked scan cache. Returns frame or None."""
    from research import data as rdata
    df = rdata.fetch_candles(base, tf, days_back=days)
    if df is None or len(df) == 0:
        return None
    os.makedirs(SCAN_CACHE_DIR, exist_ok=True)
    df.to_parquet(_scan_cache_path(base, tf), index=False, engine=rdata.PARQUET_ENGINE)
    return df


def _scan_cached_bases(tf):
    if not os.path.isdir(SCAN_CACHE_DIR):
        return []
    suffix = f"_{tf}.parquet"
    return sorted(
        name[: -len(suffix)] for name in os.listdir(SCAN_CACHE_DIR)
        if name.endswith(suffix)
    )


def _kraken_listed():
    """Bases Kraken currently offers against USD/USDT. None when offline."""
    try:
        import ccxt
        ex = ccxt.kraken({"enableRateLimit": True})
        markets = ex.load_markets()
    except Exception as e:
        _log(f"Kraken market fetch failed: {type(e).__name__}: {e}", as_json=True)
        return None

    listed = set()
    for symbol, market in markets.items():
        if not market.get("active"):
            continue
        base, _, quote = symbol.partition("/")
        if quote in ("USD", "USDT") and base not in ("USD", "USDT"):
            listed.add(base)
    return listed


def _watchlist(max_pairs=20, tf="4h"):
    """Curated order, filtered to pairs Kraken lists and the cache can serve.

    Falls back to the curated list when Kraken is unreachable, so CI keeps
    working on a network hiccup.
    """
    listed = _kraken_listed()
    candidates = list(DEFAULT_PAIRS) if listed is None else [b for b in DEFAULT_PAIRS if b in listed]
    if not candidates:
        candidates = list(DEFAULT_PAIRS)
    cached = set(_cached_bases(tf)) | set(_scan_cached_bases(tf))
    # Prioritise pairs we can score right now, keep curated order otherwise.
    ordered = [b for b in candidates if b in cached] + [b for b in candidates if b not in cached]
    return ordered[:max_pairs]


def _score_pair(base, tf="4h", fetch_missing=False):
    """Score one base. Returns (record, skip_reason); exactly one is None."""
    pair = f"{base}/USD"
    df = common.load_candles(pair, tf, None)
    if df is None:
        df = _load_scan_cache(base, tf)  # untracked wide-universe cache

    if df is None and fetch_missing:
        try:
            if base in config.ASSETS:
                from research import data as rdata
                rdata.update_asset(base, tf, days_back=FETCH_DAYS.get(tf, 365))
                df = common.load_candles(pair, tf, None)
            else:
                df = _fetch_scan_cache(base, tf, FETCH_DAYS.get(tf, 365))
        except Exception as e:
            return None, f"fetch failed ({type(e).__name__}: {e})"

    if df is None:
        return None, f"no cached {tf} candles (run: python -m research.data.update_all)"
    if len(df) < MIN_BARS:
        return None, f"only {len(df)} {tf} bars (<{MIN_BARS})"

    feats = feature_engine.extract(df, pair, tf)
    if not feats:
        return None, "feature extraction returned nothing"

    mom = feats["momentum_3_5_10_21"]
    micro = feats["micro_score"]
    vol = feats["vol_regime"]
    vspike = feats["volume_spike"]
    pos = feats["candle_position"]

    # Expected profitability: momentum + micro-structure + position.
    # Positive momentum + absorption + near support = highest score.
    score = mom * 2.0 + micro * 3.0 + vol * 1.5 + vspike * 2.0 + pos * 2.0
    return {
        "pair": pair,
        "tf": tf,
        "close": feats["last_close"],
        "momentum": round(mom, 4),
        "micro_score": round(micro, 4),
        "vol_regime": round(vol, 3),
        "volume_spike": round(vspike, 3),
        "candle_position": round(pos, 3),
        "n_bars": feats["n_bars"],
        "profit_score": round(score, 4),
    }, None


def _normalise_pair(value):
    """'btc/usd' | 'ETH-USD' | 'xrp' -> 'BTC' | 'ETH' | 'XRP'."""
    text = str(value).strip().upper().replace("-", "/").replace("_", "/")
    return text.split("/")[0]


def run(pairs=None, top_n=10, as_json=False, max_pairs=20, tf="4h", fetch_missing=False):
    """Score the universe. Returns the ranked records (may be empty)."""
    if pairs:
        candidates = [_normalise_pair(p) for p in pairs]
    else:
        candidates = _watchlist(max_pairs=max_pairs, tf=tf)

    results = []
    skipped = []
    for base in candidates[:max_pairs]:
        try:
            record, reason = _score_pair(base, tf=tf, fetch_missing=fetch_missing)
        except Exception as e:  # one bad pair must not kill the scan
            record, reason = None, f"{type(e).__name__}: {e}"
        if record:
            results.append(record)
        else:
            skipped.append({"pair": f"{base}/USD", "reason": reason or "no features"})

    results.sort(key=lambda r: r["profit_score"], reverse=True)

    _log(f"scanned {len(results)}/{len(candidates[:max_pairs])} pairs on {tf}", as_json=as_json)
    for item in skipped:
        _log(f"  skip {item['pair']}: {item['reason']}", as_json=as_json)

    if as_json:
        print(json.dumps(results[:top_n], indent=2, default=str))
        return results

    _log(f"\n=== TOP {top_n} PAIRS BY PROFITABILITY ===")
    for i, r in enumerate(results[:top_n]):
        _log(f"#{i+1} {r['pair']:12s} score={r['profit_score']:+.4f}  "
             f"mom={r['momentum']:+.4f}  micro={r['micro_score']:+.4f}  "
             f"vol={r['vol_regime']:+.3f}  close={r['close']}")
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(prog="asset_scanner.py", description=__doc__.splitlines()[0])
    ap.add_argument("--pairs", nargs="*", default=None,
                    help="explicit bases, e.g. --pairs BTC ETH (default: curated universe)")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--tf", default="4h", choices=sorted(FETCH_DAYS),
                    help="candle timeframe (default: 4h)")
    ap.add_argument("--max-pairs", type=int, default=20)
    ap.add_argument("--fetch-missing", action="store_true",
                    help="download uncached pairs (slow; writes research/data/*.parquet)")
    ap.add_argument("--json", action="store_true",
                    help="stdout is pure JSON; progress goes to stderr")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when no pair could be scored")
    args = ap.parse_args(argv)

    results = run(
        pairs=args.pairs, top_n=args.top, as_json=args.json,
        max_pairs=args.max_pairs, tf=args.tf, fetch_missing=args.fetch_missing,
    )
    if args.strict and not results:
        _log("no pairs could be scored (strict mode)", as_json=args.json)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

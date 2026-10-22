"""Trade Agent — the pre-trade warmup reader.

Before any live or paper trade, this agent:
  1. Reads all recent news (GDELT, Fear & Greed, Reddit sentiment)
  2. Reads the latest multi-agent deliberation decision
  3. Reads the current market state (price, regime, order book)
  4. Reads the AAPL 1m chart state from TradingView cache
  5. Produces a single "GO / NO-GO + context" verdict with citations

It does NOT place orders. It is the human-equivalent of reading the news,
checking the chart, and deciding whether to sit down at the desk.

Usage:
    python -m agents.trade_agent --pair BTC/USDT
    python -m agents.trade_agent --pair AAPL --equity
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from . import common, news_agent, market_agent


def _read_json(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_latest_decision():
    """Read the most recent deliberation decision."""
    d = _read_json(common.LATEST_DECISION_PATH)
    if d:
        return d
    ddir = common.DECISIONS_DIR
    if not ddir.exists():
        return None
    files = sorted(ddir.glob("*.json"), reverse=True)
    for f in files:
        if "_prompts" in f.name:
            continue
        d = _read_json(f)
        if d:
            return d
    return None


def _regime_from_market(market_report, pair):
    """Extract regime label from market agent output."""
    entry = market_report.get("pairs", {}).get(pair, {})
    tf = entry.get("timeframes", {})
    for t in ("1h", "4h", "1d"):
        if t in tf and tf[t].get("available"):
            return tf[t].get("regime"), t
    return None, None


def warmup(pair, equity=False, asof=None):
    """Run the full pre-trade warmup. Returns a verdict dict."""
    asof_dt = common.parse_utc(asof) if asof else common.utc_now()
    asof_iso = common.iso_utc(asof_dt)

    # 1. News / sentiment
    news = news_agent.analyze(asof_iso)

    # 2. Market state
    pairs = [pair]
    market = market_agent.analyze(pairs, asof_iso, live_orderbook=not equity)

    # 3. Latest deliberation
    decision = _read_latest_decision()

    # 4. Build verdict
    regime, tf_used = _regime_from_market(market, pair)
    fng = news.get("fng") or {}
    gdelt = news.get("gdelt") or {}

    # Scoring: simple rule-based GO/NO-GO
    blockers = []
    score = 0

    if regime == "bull":
        score += 2
    elif regime == "bear":
        score -= 2
        blockers.append(f"regime=bear ({tf_used})")

    fng_val = fng.get("value")
    if fng_val is not None:
        if fng_val <= 25:
            score += 1
        elif fng_val >= 75:
            score -= 1
            blockers.append(f"fng={fng_val} (extreme greed)")

    # GDELT tone
    for q, data in gdelt.items():
        tone = data.get("tone_7d")
        if tone is not None and tone < 0:
            score -= 1
            blockers.append(f"gdelt[{q}] tone_7d={tone} (negative)")

    # Deliberation veto
    dec_pairs = (decision or {}).get("decision", {}).get("pairs", {})
    dec = dec_pairs.get(pair, {})
    if dec.get("action") == "block":
        score -= 3
        blockers.append(f"deliberation=block: {dec.get('rationale', 'no reason')}")

    verdict = "GO" if score >= 1 else "NO-GO"

    result = {
        "asof": asof_iso,
        "pair": pair,
        "equity": equity,
        "verdict": verdict,
        "score": score,
        "regime": regime,
        "regime_tf": tf_used,
        "fng": fng,
        "fng_7d_change": news.get("fng_7d_change"),
        "gdelt": gdelt,
        "reddit": news.get("reddit"),
        "market": market,
        "deliberation": {
            "asof": (decision or {}).get("asof"),
            "action": dec.get("action"),
            "size": dec.get("size"),
            "confidence": dec.get("confidence"),
            "rationale": dec.get("rationale"),
        },
        "blockers": blockers,
    }
    return result


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="python -m agents.trade_agent")
    p.add_argument("--pair", default="BTC/USDT")
    p.add_argument("--equity", action="store_true")
    p.add_argument("--asof", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    result = warmup(args.pair, equity=args.equity, asof=args.asof)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"=== Trade Warmup: {args.pair} ===")
        print(f"  Asof:      {result['asof']}")
        print(f"  Verdict:   {result['verdict']}  (score={result['score']})")
        print(f"  Regime:    {result['regime']} ({result['regime_tf']})")
        fng = result['fng'] or {}
        print(f"  F&G:       {fng.get('value')} ({fng.get('classification')})")
        print(f"  F&G 7d ch: {result['fng_7d_change']}")
        dec = result['deliberation']
        print(f"  Deliberation: {dec.get('action')} size={dec.get('size')} conf={dec.get('confidence')}")
        if result['blockers']:
            print(f"  Blockers:")
            for b in result['blockers']:
                print(f"    - {b}")
        else:
            print(f"  Blockers:   none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

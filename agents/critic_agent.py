"""Critic agent: red-teams the Analyst candidate. Must attempt to falsify."""
from . import common


def _evidence_for(market, candidate_pair):
    tf = market.get("pairs", {}).get(candidate_pair, {}).get("timeframes", {})
    return [
        f"regime_1h={tf.get('1h', {}).get('regime')}",
        f"regime_4h={tf.get('4h', {}).get('regime')}",
        f"atr_pct_1h={tf.get('1h', {}).get('atr_pct_14')}",
        f"dist_to_high20_1h={tf.get('1h', {}).get('dist_to_high20_pct')}",
    ]


def analyze(asof, market_report, analyst_recommendation):
    """Return a blackboard entry for the critic.

    analyst_recommendation: dict pair-> {action,size,confidence,rationale}
    """
    claims = []
    blockers = []
    pair_recs = {}
    for pair, rec in (analyst_recommendation or {}).items():
        action = rec.get("action", "block")
        ev = _evidence_for(market_report, pair)
        tf = market_report.get("pairs", {}).get(pair, {}).get("timeframes", {})
        # Availability-aware regime check: equities/FX legitimately have only
        # 1d data, so a missing intraday regime must not veto them. Crypto with
        # a bear regime, or any symbol with NO regime data at all, still blocks.
        issues = []
        if action == "allow":
            regimes = {
                name: (tf.get(name) or {}).get("regime")
                for name in ("1h", "4h", "1d")
                if (tf.get(name) or {}).get("available")
            }
            regimes = {k: v for k, v in regimes.items() if v}
            if not regimes:
                issues.append("no regime data available (fail closed)")
            else:
                bears = ",".join(sorted(k for k, v in regimes.items() if v == "bear"))
                if bears:
                    issues.append(f"bear regime on {bears}")
                elif not any(v == "bull" for v in regimes.values()):
                    issues.append("no bull regime on any available timeframe")
        atr = (tf.get("1h") or {}).get("atr_pct_14")
        if atr is None:
            atr = (tf.get("4h") or {}).get("atr_pct_14")
        if atr is not None and atr > 5.0:
            issues.append(f"ATR {atr}% high -> slippage risk")
        if issues:
            rec_out = "block"
            blockers.extend(issues)
            rationale = "critic veto: " + "; ".join(issues)
        else:
            rec_out = action
            rationale = "critic: no falsifying evidence found after checking regime + ATR"
        claims.append({
            "text": f"Red-teamed {pair}: {rationale}",
            "evidence": ev,
        })
        pair_recs[pair] = rec_out

    recommendation = "block" if blockers else "allow"
    confidence = 0.6 if blockers else 0.7
    return {
        "agent": "critic",
        "round": None,  # caller sets
        "claims": claims if claims else [{"text": "no pairs to critique", "evidence": ["n/a"]}],
        "recommendation": recommendation,
        "confidence": confidence,
        "blockers": blockers,
        "pair_recommendations": pair_recs,
    }

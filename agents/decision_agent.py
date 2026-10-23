import hashlib
import json
import random

from . import common, market_agent, news_agent, risk_agent, session_agent
from . import daily_learning, evidence_gate, vibe_evidence

INSTRUCTION = (
    "You are a risk veto layer for a crypto spot trading bot (Bybit, USDT pairs). "
    "Every number below is precomputed by deterministic Python agents; your job is only to interpret them. "
    "You may only ALLOW or BLOCK entries per pair and optionally shrink the position size. "
    "You can never place, modify or close orders. "
    "When in doubt, block. "
    "If an EVIDENCE block is present, your rationale must cite at least one alpha factor or "
    "asset-scan number from it verbatim; never invent a number that is not in DATA or EVIDENCE. "
    "Respond with ONLY one JSON object and nothing else, no prose and no code fences, using exactly this schema: "
    '{"pairs": {"<PAIR>": {"action": "allow" or "block", "size": <0.0-1.0>, '
    '"confidence": <0.0-1.0>, "rationale": "<short text>"}}, "followups": ["<question>", "..."]}. '
    "Include one entry for every requested pair. size is a fraction of the normal stake. "
    "followups may be an empty list if no further data is needed."
)


def _evidence_payload():
    """GitHub-produced evidence the analyst must reason over (may be empty)."""
    payload = {}
    try:
        summary = vibe_evidence.summarize()
    except Exception:
        summary = None
    if summary and summary.get("top"):
        payload["alpha_bench"] = {
            "zoo": summary.get("zoo"),
            "universe": summary.get("universe"),
            "period": summary.get("period"),
            "age_hours": summary.get("age_hours"),
            "top": summary["top"],
            "caveats": summary.get("caveats"),
        }
    scan = evidence_gate.load_asset_scan()
    if scan:
        ranked = sorted(
            (row for row in scan if isinstance(row, dict)
             and isinstance(row.get("profit_score"), (int, float))),
            key=lambda row: row["profit_score"],
            reverse=True,
        )
        payload["asset_scan"] = [
            {"pair": row.get("pair"), "profit_score": row.get("profit_score"),
             "momentum": row.get("momentum"), "micro_score": row.get("micro_score")}
            for row in ranked[:10]
        ]
    try:
        lessons = daily_learning.prompt_block()
    except Exception:
        lessons = ""
    if lessons:
        payload["historical_lessons"] = lessons
    return payload


def _asset_mapping(pairs, asof_dt):
    seed = int(
        hashlib.sha256(common.iso_utc(asof_dt).encode("utf-8")).hexdigest(), 16
    )
    rng = random.Random(seed)
    order = list(pairs)
    rng.shuffle(order)
    return {pair: f"ASSET_{index + 1}" for index, pair in enumerate(order)}


def _ratio(value, base):
    try:
        value = float(value)
        base = float(base)
    except (TypeError, ValueError):
        return None
    if not base:
        return None
    return common.rnd(value / base - 1.0)


def _anonymize_timeframe(tf):
    if not isinstance(tf, dict) or not tf.get("available"):
        return {"available": False}
    close = tf.get("close")
    ema50 = tf.get("ema50")
    ema200 = tf.get("ema200")
    return {
        "available": True,
        "close_over_ema50_minus_1": _ratio(close, ema50),
        "close_over_ema200_minus_1": _ratio(close, ema200),
        "ema50_over_ema200_minus_1": _ratio(ema50, ema200),
        "ema50_slope_pct": tf.get("ema50_slope"),
        "dist_to_high20_pct": tf.get("dist_to_high20_pct"),
        "dist_to_low20_pct": tf.get("dist_to_low20_pct"),
        "atr_pct": tf.get("atr_pct_14"),
        "volume_z": tf.get("volume_z_48"),
        "regime": tf.get("regime"),
    }


def _anonymize_market(market, mapping):
    out = {"pairs": {}}
    for real, asset in mapping.items():
        entry = market.get("pairs", {}).get(real, {})
        anon_entry = {
            "timeframes": {
                tf: _anonymize_timeframe(value)
                for tf, value in entry.get("timeframes", {}).items()
            }
        }
        if "orderbook" in entry:
            orderbook = entry.get("orderbook")
            if isinstance(orderbook, dict):
                anon_entry["orderbook"] = {"spread_pct": orderbook.get("spread_pct")}
            else:
                anon_entry["orderbook"] = None
        out["pairs"][asset] = anon_entry
    return out


def _anonymize_news(news):
    fng = news.get("fng")
    anon_fng = None
    if isinstance(fng, dict):
        anon_fng = {
            "value": fng.get("value"),
            "classification": fng.get("classification"),
        }
    gdelt = news.get("gdelt")
    anon_gdelt = {}
    if isinstance(gdelt, dict):
        for query, slot in gdelt.items():
            if isinstance(slot, dict):
                anon_gdelt[query] = {
                    "tone_24h": slot.get("tone_24h"),
                    "tone_7d": slot.get("tone_7d"),
                    "n_24h": slot.get("n_24h"),
                    "n_7d": slot.get("n_7d"),
                }
    reddit = news.get("reddit")
    anon_reddit = None
    if isinstance(reddit, dict):
        anon_reddit = {
            key: value for key, value in reddit.items() if not isinstance(value, str)
        }
    return {
        "fng": anon_fng,
        "fng_7d_change": news.get("fng_7d_change"),
        "gdelt": anon_gdelt,
        "reddit": anon_reddit,
    }


def _anonymize_session(session, mapping):
    out = {"current_session": session.get("current_session"), "pairs": {}}
    for real, asset in mapping.items():
        entry = session.get("pairs", {}).get(real, {})
        if isinstance(entry, dict) and entry.get("available"):
            out["pairs"][asset] = {"available": True, "session": entry.get("session")}
        else:
            out["pairs"][asset] = {"available": False}
    return out


def _anonymize_risk(risk):
    btc = risk.get("btc")
    reference = None
    if isinstance(btc, dict):
        reference = {
            "available": btc.get("available"),
            "below_ema200": btc.get("below_ema200"),
        }
    account = risk.get("account")
    anon_account = None
    if isinstance(account, dict):
        anon_account = {"open_trades": account.get("open_trades")}
    reasons = risk.get("reasons")
    anon_reasons = []
    if isinstance(reasons, list):
        anon_reasons = [
            str(reason).replace("BTC", "reference asset") for reason in reasons
        ]
    return {
        "reference_asset_regime": reference,
        "account": anon_account,
        "drawdown": risk.get("drawdown"),
        "size_cap": risk.get("size_cap"),
        "reasons": anon_reasons,
    }


def _payload(pairs, reports, anonymize, mapping):
    if anonymize:
        return {
            "pairs": [mapping[pair] for pair in pairs],
            "market": _anonymize_market(reports["market"], mapping),
            "news": _anonymize_news(reports["news"]),
            "session": _anonymize_session(reports["session"], mapping),
            "risk": _anonymize_risk(reports["risk"]),
        }
    return {
        "asof": reports["market"]["asof"],
        "pairs": list(pairs),
        "market": reports["market"],
        "news": reports["news"],
        "session": reports["session"],
        "risk": reports["risk"],
    }


def _build_prompt(pairs, asof, reports, anonymize=False, mapping=None, evidence=None):
    payload = _payload(pairs, reports, anonymize, mapping)
    prompt = (
        INSTRUCTION
        + "\nDATA: "
        + json.dumps(payload, default=str)
    )
    if evidence:
        prompt += "\nEVIDENCE: " + json.dumps(evidence, default=str)
    return prompt + "\nReturn only the JSON object now."


def _followup_prompt(base_prompt, followups, reports, anonymize=False, mapping=None):
    if anonymize:
        detail = {
            "market": _anonymize_market(reports["market"], mapping),
            "session": _anonymize_session(reports["session"], mapping),
        }
    else:
        detail = {
            "market": reports["market"],
            "session": reports["session"],
        }
    return (
        base_prompt
        + "\nFOLLOW-UP QUESTIONS: "
        + json.dumps(list(followups), default=str)
        + "\nFULL MARKET AND SESSION DETAIL: "
        + json.dumps(detail, default=str)
        + "\nAnswer again with the same JSON schema and only that JSON."
    )


def _validate_pair(item, size_cap):
    if not isinstance(item, dict):
        return {
            "action": "block",
            "size": 0.0,
            "confidence": 0.0,
            "rationale": "missing or invalid entry",
        }
    action = item.get("action")
    if action not in ("allow", "block"):
        action = "block"
    try:
        size = float(item.get("size"))
    except (TypeError, ValueError):
        size = 0.0
    if size < 0.0:
        size = 0.0
    if size > size_cap:
        size = size_cap
    if action == "block" or size_cap <= 0:
        action = "block"
        size = 0.0
    try:
        confidence = float(item.get("confidence"))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = min(1.0, max(0.0, confidence))
    rationale = item.get("rationale")
    if not isinstance(rationale, str):
        rationale = ""
    return {
        "action": action,
        "size": common.rnd(size),
        "confidence": common.rnd(confidence),
        "rationale": rationale,
    }


def _normalize(obj, pairs, size_cap):
    raw_pairs = obj.get("pairs") if isinstance(obj, dict) else None
    if not isinstance(raw_pairs, dict):
        raw_pairs = {}
    return {pair: _validate_pair(raw_pairs.get(pair), size_cap) for pair in pairs}


def _fallback(pairs, size_cap, market):
    result = {}
    for pair in pairs:
        timeframes = market.get("pairs", {}).get(pair, {}).get("timeframes", {})
        # Prefer the highest-signal available timeframe; equities/FX only have 1d.
        regime = None
        used_tf = None
        for name in ("4h", "1d", "1h"):
            slot = timeframes.get(name) or {}
            if slot.get("available") and slot.get("regime"):
                regime = slot["regime"]
                used_tf = name
                break
        if size_cap > 0 and regime == "bull":
            result[pair] = {
                "action": "allow",
                "size": common.rnd(size_cap),
                "confidence": 0.5,
                "rationale": f"fallback rule: {used_tf} regime bull",
            }
        else:
            result[pair] = {
                "action": "block",
                "size": 0.0,
                "confidence": 0.5,
                "rationale": (
                    f"fallback rule: {used_tf or 'no'} regime={regime}, "
                    f"size_cap={size_cap}"
                ),
            }
    return result


def decide(
    pairs,
    asof,
    use_llm=True,
    api_url=None,
    live_orderbook=False,
    anonymize=False,
):
    asof_dt = common.parse_utc(asof)
    reports = {
        "market": market_agent.analyze(pairs, asof_dt, live_orderbook=live_orderbook),
        "news": news_agent.analyze(asof_dt),
        "session": session_agent.analyze(pairs, asof_dt),
        "risk": risk_agent.analyze(asof_dt, api_url=api_url),
    }
    mapping = _asset_mapping(pairs, asof_dt) if anonymize else None
    size_cap = reports["risk"].get("size_cap", 0.0)
    prompts = []
    raws = []
    followups = []
    best = None
    model_used = None
    try:
        evidence = _evidence_payload()
    except Exception:  # evidence is context, never a reason to fail a decision
        evidence = {}
    if use_llm:
        prompt = _build_prompt(
            pairs, asof_dt, reports, anonymize=anonymize, mapping=mapping,
            evidence=evidence,
        )
        prompts.append(prompt)
        for round_index in range(3):
            obj, raw, model = common.call_llm(prompt, timeout=300)
            raws.append(raw)
            if model:
                model_used = model
            if obj is None:
                break
            best = obj
            followups = obj.get("followups")
            if not isinstance(followups, list):
                followups = []
            followups = [f for f in followups if isinstance(f, str) and f.strip()]
            if not followups or round_index >= 2:
                break
            prompt = _followup_prompt(
                prompt, followups, reports, anonymize=anonymize, mapping=mapping
            )
            prompts.append(prompt)
    if best is not None:
        source = "llm"
        if anonymize:
            labels = [mapping[pair] for pair in pairs]
            normalized = _normalize(best, labels, size_cap)
            decision_pairs = {pair: normalized[mapping[pair]] for pair in pairs}
        else:
            decision_pairs = _normalize(best, pairs, size_cap)
    else:
        source = "fallback"
        model_used = None
        decision_pairs = _fallback(pairs, size_cap, reports["market"])
    return {
        "asof": common.iso_utc(asof_dt),
        "source": source,
        "model": model_used,
        "pairs": decision_pairs,
        "followups": followups,
        "reports": reports,
        "prompts": prompts,
        "raw": raws,
        "anonymize": bool(anonymize),
        "mapping": mapping,
        "evidence": evidence,
    }

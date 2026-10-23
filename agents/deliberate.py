"""Deliberative orchestrator: blackboard + critic + auditor + synthesizer.

Wraps decision_agent.decide() outputs into a structured multi-agent
deliberation. Keeps the existing decide() as the data-gathering/LLM step,
then adds red-team + audit + synthesis on top.
"""
import sys

from . import common, decision_agent, critic_agent, auditor_agent, synthesizer_agent, blackboard as bb
from . import vibe_evidence


def run(pairs, asof, use_llm=True, api_url=None, live_orderbook=False, anonymize=False):
    asof_dt = common.parse_utc(asof) if not hasattr(asof, "tzinfo") else asof
    # Gather reports + LLM decision via existing pipeline
    decision = decision_agent.decide(
        pairs, asof_dt, use_llm=use_llm, api_url=api_url,
        live_orderbook=live_orderbook, anonymize=anonymize,
    )
    reports = decision["reports"]
    market = reports["market"]
    risk = reports["risk"]
    analyst_rec = decision["pairs"]  # treat LLM output as analyst recommendation
    b = bb.Blackboard(common.iso_utc(asof_dt), pairs)

    # Round 1: analyst (from decide()) + risk + critic
    analyst_entry = {
        "agent": "analyst",
        "round": 1,
        "claims": [{"text": f"LLM decision source={decision['source']}", "evidence": ["decision.pairs"]}],
        "recommendation": "allow" if any(v.get("action") == "allow" for v in analyst_rec.values()) else "block",
        "confidence": common.rnd(sum(v.get("confidence", 0.0) for v in analyst_rec.values()) / max(1, len(analyst_rec))),
        "blockers": [],
        "pair_recommendations": {p: v.get("action", "block") for p, v in analyst_rec.items()},
    }
    risk_entry = {
        "agent": "risk",
        "round": 1,
        "claims": [{"text": f"size_cap={risk.get('size_cap')}", "evidence": [f"drawdown={risk.get('drawdown')}", f"reasons={risk.get('reasons')}"]}],
        "recommendation": "allow" if risk.get("size_cap", 0) > 0 else "block",
        "confidence": 0.9,
        "blockers": risk.get("reasons", []),
        "pair_recommendations": {},
    }
    critic_raw = critic_agent.analyze(asof_dt, market, analyst_rec)
    critic_raw["round"] = 1
    b.add(analyst_entry)
    b.add(risk_entry)
    b.add(critic_raw)

    # Cite the latest Vibe-Trading alpha benchmark when one has been committed
    # by the "Vibe-Trading research" workflow. A missing artifact is normal and
    # must not fail deliberation -- this is context, not a veto.
    try:
        vibe = vibe_evidence.summarize()
        vibe_entry = vibe_evidence.blackboard_entry(vibe)
    except Exception as e:  # evidence must never break a decision
        print(f"vibe-factors: evidence unavailable ({type(e).__name__}: {e})", file=sys.stderr)
        vibe, vibe_entry = None, None
    if vibe_entry:
        b.add(vibe_entry)

    # Round 2: synthesizer + auditor
    synth_entry, decision_pairs = synthesizer_agent.analyze(
        asof_dt, market, risk, analyst_rec, critic_raw.get("pair_recommendations", {}), 2
    )
    synth_entry["round"] = 2
    audit_raw = auditor_agent.analyze(asof_dt, b.round_entries(1))
    audit_raw["round"] = 2
    b.add(synth_entry)
    b.add(audit_raw)

    # If auditor blocks, force block all
    if audit_raw["recommendation"] == "block":
        for p in decision_pairs:
            decision_pairs[p]["action"] = "block"
            decision_pairs[p]["size"] = 0.0
            decision_pairs[p]["rationale"] = "auditor veto: " + "; ".join(audit_raw["blockers"])

    b.convergence = b.converged()
    # override convergence if auditor blocked
    if audit_raw["recommendation"] == "block":
        b.convergence = False

    decision["pairs"] = decision_pairs
    decision["vibe_factors"] = vibe
    decision["deliberation"] = b.to_dict()
    return decision, b


# --- CLI entrypoint -------------------------------------------------------
# The GitHub Actions workflow calls `python -m agents.deliberate`. Without this
# block Python imports the module and exits 0 without running anything, so the
# workflow reported "success" every cycle while producing zero decisions.
def main(argv=None):
    import argparse
    import json

    parser = argparse.ArgumentParser(prog="python -m agents.deliberate")
    parser.add_argument("--pairs", default=None)
    parser.add_argument("--asof", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--live-orderbook", action="store_true")
    parser.add_argument("--anonymize", action="store_true")
    args = parser.parse_args(argv)

    # Reuse run_cycle's pair parsing / config whitelist logic.
    from .run_cycle import default_pairs, parse_pairs

    pairs = parse_pairs(args.pairs)
    use_llm = not args.no_llm
    live = args.asof is None
    asof_dt = common.utc_now() if live else common.parse_utc(args.asof)

    decision, b = run(
        pairs,
        asof_dt,
        use_llm=use_llm,
        api_url=args.api_url,
        live_orderbook=args.live_orderbook,
        anonymize=args.anonymize,
    )

    generated_at = common.iso_utc(common.utc_now())
    common.DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = common.DECISIONS_DIR / (asof_dt.strftime("%Y-%m-%d_%H%M") + ".json")
    record = {
        "asof": decision["asof"],
        "generated_at": generated_at,
        "pairs": list(pairs),
        "live_orderbook": bool(args.live_orderbook),
        "use_llm": bool(use_llm),
        "anonymize": bool(args.anonymize),
        "inputs": decision["reports"],
        "prompts": decision["prompts"],
        "raw": decision["raw"],
        "model": decision["model"],
        "decision": {
            "source": decision["source"],
            "followups": decision["followups"],
            "pairs": decision["pairs"],
        },
        "deliberation": b.to_dict(),
        "vibe_factors": decision.get("vibe_factors"),
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=str)

    # Always publish the latest decision pointer: the Render webhook and the
    # PC-off evidence gate read it, including for scheduled (non-live) runs.
    common.LATEST_DECISION_PATH.parent.mkdir(parents=True, exist_ok=True)
    latest = {
        "asof": decision["asof"],
        "generated_at": generated_at,
        "source": decision["source"],
        "pairs": decision["pairs"],
        # Evidence carried into the live gate (Render/PC reads this file).
        "vibe_factors": decision.get("vibe_factors"),
        "evidence": decision.get("evidence"),
    }
    with open(common.LATEST_DECISION_PATH, "w", encoding="utf-8") as fh:
        json.dump(latest, fh, indent=2, default=str)

    for pair in pairs:
        item = decision["pairs"].get(pair, {})
        print(
            f"{pair} {item.get('action', 'block')} "
            f"size={item.get('size', 0.0)} "
            f"conf={item.get('confidence', 0.0)} "
            f"- {item.get('rationale', '')}"
        )
    print(f"wrote {out_path}")
    print(f"deliberation rounds: {sorted(b.rounds.keys())}")
    vibe = decision.get("vibe_factors")
    if vibe and vibe.get("top"):
        best = vibe["top"][0]
        print(
            f"vibe-factors: {best['alpha']} IR={best['ir']} IC_mean={best['ic_mean']} "
            f"({vibe.get('zoo')}/{vibe.get('universe')} {vibe.get('period')})"
        )
    else:
        print("vibe-factors: no benchmark artifact yet (run the 'Vibe-Trading research' workflow)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

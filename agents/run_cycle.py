import argparse
import json

from . import common, decision_agent


def default_pairs():
    try:
        with open(common.CONFIG_PATH, encoding="utf-8") as fh:
            cfg = json.load(fh)
        whitelist = cfg.get("exchange", {}).get("pair_whitelist")
        if isinstance(whitelist, list) and whitelist:
            return [str(pair) for pair in whitelist]
    except Exception:
        pass
    return ["BTC/USDT"]


def parse_pairs(value):
    if not value:
        return default_pairs()
    raw = value.replace(" ", ",")
    return [part.strip() for part in raw.split(",") if part.strip()]


def build_record(decision, pairs, use_llm, live_orderbook, generated_at, anonymize=False):
    record = {
        "asof": decision["asof"],
        "generated_at": generated_at,
        "pairs": list(pairs),
        "live_orderbook": bool(live_orderbook),
        "use_llm": bool(use_llm),
        "anonymize": bool(anonymize),
        "inputs": decision["reports"],
        "prompts": decision["prompts"],
        "raw": decision["raw"],
        "model": decision["model"],
        "decision": {
            "source": decision["source"],
            "followups": decision["followups"],
            "pairs": decision["pairs"],
        },
    }
    if anonymize:
        record["anonymization"] = {"mapping": decision.get("mapping")}
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m agents.run_cycle")
    parser.add_argument("--pairs", default=None)
    parser.add_argument("--asof", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--live-orderbook", action="store_true")
    parser.add_argument("--anonymize", action="store_true")
    parser.add_argument(
        "--single-agent",
        action="store_true",
        help="Skip the multi-agent deliberation layer (analyst only).",
    )
    args = parser.parse_args(argv)

    pairs = parse_pairs(args.pairs)
    use_llm = not args.no_llm
    live = args.asof is None
    asof_dt = common.utc_now() if live else common.parse_utc(args.asof)

    blackboard = None
    if args.single_agent:
        decision = decision_agent.decide(
            pairs,
            asof_dt,
            use_llm=use_llm,
            api_url=args.api_url,
            live_orderbook=args.live_orderbook,
            anonymize=args.anonymize,
        )
    else:
        # Full multi-agent path: analyst -> risk -> critic -> synthesizer -> auditor.
        # Deliberation is the default because the critic/auditor veto layer is the
        # point of this system; --single-agent is the explicit opt-out.
        from . import deliberate as deliberate_mod

        decision, blackboard = deliberate_mod.run(
            pairs,
            asof_dt,
            use_llm=use_llm,
            api_url=args.api_url,
            live_orderbook=args.live_orderbook,
            anonymize=args.anonymize,
        )

    generated_at = common.iso_utc(common.utc_now())
    record = build_record(
        decision, pairs, use_llm, args.live_orderbook, generated_at, anonymize=args.anonymize
    )
    if blackboard is not None:
        record["deliberation"] = blackboard.to_dict()
    common.DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = common.DECISIONS_DIR / (asof_dt.strftime("%Y-%m-%d_%H%M") + ".json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=str)

    if live:
        common.LATEST_DECISION_PATH.parent.mkdir(parents=True, exist_ok=True)
        latest = {
            "asof": decision["asof"],
            "generated_at": generated_at,
            "source": decision["source"],
            "pairs": decision["pairs"],
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
    if blackboard is not None:
        print(f"deliberation rounds: {sorted(blackboard.rounds.keys())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

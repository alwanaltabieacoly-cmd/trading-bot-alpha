#!/usr/bin/env python3
"""One-page trading brief you can read and act on (midday or end of day).

Merges every committed artifact into a single markdown file:

  * evidence-gate verdict per deliberated symbol (allow/block + reason)
  * multi-asset scan leaders (crypto + equities + FX)
  * the positive shortlist deliberation used
  * latest Vibe-Trading alpha evidence
  * daily-learning accuracy + active lessons

Writes research/reports/brief/YYYY-MM-DD.md and prints it.

Usage:
    python scripts/daily_brief.py --write
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents import daily_learning, evidence_gate, vibe_evidence  # noqa: E402

BRIEF_DIR = ROOT / "research" / "reports" / "brief"
SCAN_PATH = ROOT / "research" / "reports" / "asset_scan.json"
SHORTLIST_PATH = ROOT / "research" / "reports" / "scan_shortlist.json"
TOP_SCAN = 7
TOP_ALPHAS = 3


def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def collect(now=None):
    now = now or datetime.now(timezone.utc)
    payload = {
        "generated_at": now.isoformat(),
        "date": now.date().isoformat(),
        "scan": (_load_json(SCAN_PATH) or [])[:TOP_SCAN],
        "shortlist": (_load_json(SHORTLIST_PATH) or {}).get("decision_pairs") or [],
        "decision": None,
        "gate": {},
        "vibe": None,
        "learning": None,
    }

    record, path = evidence_gate.newest_decision()
    payload["decision"] = {
        "path": path.as_posix() if path else None,
        "generated_at": (record or {}).get("generated_at") or (record or {}).get("asof"),
        "pairs": [p for p in (evidence_gate._decision_pairs(record) or {})],
    } if record else None

    for pair in (payload["decision"] or {}).get("pairs", []):
        try:
            result = evidence_gate.check_entry(pair)
        except Exception as e:  # gate must never break the brief
            result = {"allowed": False, "reasons": [f"gate error: {type(e).__name__}"], "evidence": {}}
        pair_entry = result.get("evidence", {}).get("decision_pair") or {}
        action = pair_entry.get("action")
        size = pair_entry.get("size")
        evidence_ok = bool(result.get("allowed"))
        # Effective entry needs ALL of: fresh evidence, deliberation allow, size > 0.
        entry_allowed = (
            evidence_ok and action == "allow"
            and isinstance(size, (int, float)) and size > 0
        )
        reasons = list(result.get("reasons") or [])
        if evidence_ok and not entry_allowed:
            if action != "allow":
                reasons.append(f"deliberation {action or 'missing'} ({pair_entry.get('rationale', '')})")
            elif not (isinstance(size, (int, float)) and size > 0):
                reasons.append(f"deliberation size={size}")
        payload["gate"][pair] = {
            "entry": entry_allowed,
            "evidence_ok": evidence_ok,
            "reasons": reasons,
            "scan_score": (result.get("evidence", {}).get("scan") or {}).get("profit_score"),
            "action": action,
            "size": size,
        }

    try:
        summary = vibe_evidence.summarize()
        if summary:
            payload["vibe"] = {
                "zoo": summary.get("zoo"), "universe": summary.get("universe"),
                "period": summary.get("period"), "age_hours": summary.get("age_hours"),
                "top": (summary.get("top") or [])[:TOP_ALPHAS],
            }
    except Exception:
        payload["vibe"] = None

    try:
        metrics = daily_learning.learn()
        payload["learning"] = {
            "n": metrics["overall"]["n"],
            "accuracy": metrics["overall"]["accuracy"],
            "lessons": [item["text"] for item in metrics.get("lessons") or []],
        }
    except Exception:
        payload["learning"] = None

    return payload


def build_markdown(payload):
    lines = [f"# Trading brief - {payload['date']}", ""]
    decision = payload.get("decision")
    if decision:
        lines.append(f"Decision record: `{decision['path']}` (generated {decision['generated_at']})")
    else:
        lines.append("Decision record: **none** - entries fail closed.")
    lines.append("")

    lines.append("## Gate verdicts (can we enter?)")
    if payload.get("gate"):
        lines.append("")
        lines.append("| symbol | entry | evidence | deliberation | size | scan | reason |")
        lines.append("|---|---|---|---|---|---|---|")
        for symbol, item in payload["gate"].items():
            entry = "ALLOW" if item.get("entry") else "BLOCK"
            evidence = "ok" if item.get("evidence_ok") else "fail"
            reason = "; ".join(item.get("reasons") or [])[:140] or "-"
            lines.append(
                f"| {symbol} | {entry} | {evidence} | {item.get('action') or '-'} | "
                f"{item.get('size') if item.get('size') is not None else '-'} | "
                f"{item.get('scan_score') if item.get('scan_score') is not None else '-'} | {reason} |"
            )
    else:
        lines.append("")
        lines.append("No deliberated symbols in the latest decision.")
    lines.append("")

    lines.append("## Scan leaders (all asset classes)")
    if payload.get("scan"):
        lines.append("")
        lines.append("| symbol | class | score | momentum | micro |")
        lines.append("|---|---|---|---|---|")
        for row in payload["scan"]:
            lines.append(
                f"| {row.get('pair')} | {row.get('asset_class', '?')} | "
                f"{row.get('profit_score')} | {row.get('momentum')} | {row.get('micro_score')} |"
            )
    else:
        lines.append("")
        lines.append("No scan artifact yet.")
    lines.append("")

    lines.append("## Deliberation shortlist")
    lines.append("")
    lines.append(", ".join(payload.get("shortlist") or []) or "empty (no positive scores)")
    lines.append("")

    lines.append("## Alpha evidence (Vibe-Trading)")
    vibe = payload.get("vibe")
    if vibe:
        lines.append("")
        lines.append(f"{vibe['zoo']} / {vibe['universe']} {vibe['period']} (age {vibe['age_hours']}h)")
        lines.append("")
        for row in vibe["top"]:
            lines.append(f"- {row['alpha']}: IR {row['ir']}, IC mean {row['ic_mean']}, N {row['ic_count']}")
    else:
        lines.append("")
        lines.append("No alpha artifact yet.")
    lines.append("")

    lines.append("## Learning")
    learning = payload.get("learning")
    if learning:
        lines.append("")
        lines.append(f"Labelled outcomes: {learning['n']} - accuracy {learning['accuracy']}")
        if learning["lessons"]:
            lines.append("")
            lines += [f"- {lesson}" for lesson in learning["lessons"]]
    else:
        lines.append("")
        lines.append("No learning digest yet.")
    lines.append("")

    lines.append("## How to act")
    lines.append("")
    lines.append("- Only `ALLOW` rows are eligible; every BLOCK row states its reason.")
    lines.append("- Paper first: this brief is evidence, not permission.")
    lines.append("- Re-run manually: `gh workflow run Deliberate` then `gh workflow run \"Daily learning\"`.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scripts/daily_brief.py")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = collect()
    markdown = build_markdown(payload)
    if args.write:
        BRIEF_DIR.mkdir(parents=True, exist_ok=True)
        path = BRIEF_DIR / f"{payload['date']}.md"
        path.write_text(markdown, encoding="utf-8")
        print(f"wrote {path}")
    print(markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())

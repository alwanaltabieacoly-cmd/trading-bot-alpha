"""Fail-closed evidence gate for live/paper entries.

Everything here is stdlib-only on purpose: the webhook, the analyst prompt and
the tests all share it, and none of them should gain a new dependency.

The gate enforces the rule the operator asked for: no entry without fresh,
GitHub-produced evidence. Each check either passes or blocks with an explicit
reason -- nothing is silently assumed.

Environment knobs (all optional):
    TV_EVIDENCE_MAX_AGE_HOURS   max age of a deliberation decision   (default 30)
    TV_VIBE_MAX_AGE_HOURS       max age of the alpha-bench artifact   (default 48)
    TV_REQUIRE_VIBE             "0" disables the alpha-evidence check (default 1)
    TV_REQUIRE_POSITIVE_SCAN    "0" disables the negative-scan veto   (default 1)
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DECISIONS_DIR = PROJECT_ROOT / "reports" / "decisions"
LATEST_DECISION_PATH = PROJECT_ROOT / "user_data" / "decisions" / "latest.json"
SCAN_PATH = PROJECT_ROOT / "research" / "reports" / "asset_scan.json"
VIBE_DIR = PROJECT_ROOT / "research" / "reports" / "vibe"

# Optional read-through to GitHub raw, so a stale checkout (e.g. a Render
# container deployed before the newest commit) still gates on the latest
# committed evidence. Unset -> local files only.
REMOTE_BASE = os.getenv("TB_EVIDENCE_REMOTE", "").strip().rstrip("/")
REMOTE_TIMEOUT = 8.0
REMOTE_DECISION = "user_data/decisions/latest.json"
REMOTE_SCAN = "research/reports/asset_scan.json"
REMOTE_VIBE = "research/reports/vibe/latest.json"


def _env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_flag(name, default=True):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in ("0", "false", "no", "off")


MAX_DECISION_AGE_H = _env_float("TV_EVIDENCE_MAX_AGE_HOURS", 30.0)
MAX_VIBE_AGE_H = _env_float("TV_VIBE_MAX_AGE_HOURS", 48.0)
REQUIRE_VIBE = _env_flag("TV_REQUIRE_VIBE", True)
REQUIRE_POSITIVE_SCAN = _env_flag("TV_REQUIRE_POSITIVE_SCAN", True)


def _parse_ts(value):
    if not value:
        return None
    try:
        text = str(value).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _age_hours(value, now=None):
    dt = _parse_ts(value)
    if dt is None:
        return None
    now = now or datetime.now(timezone.utc)
    return round((now - dt).total_seconds() / 3600.0, 2)


def newest_decision(decisions_dir=None):
    """Newest full decision record (the one carrying vibe evidence)."""
    directory = Path(decisions_dir) if decisions_dir else DECISIONS_DIR
    try:
        if not directory.is_dir():
            return None, None
        files = [p for p in directory.glob("*.json") if p.is_file()]
        if not files:
            return None, None
        path = max(files, key=lambda p: p.stat().st_mtime)
        return json.loads(path.read_text(encoding="utf-8")), path
    except (OSError, ValueError):
        return None, None


def load_asset_scan(scan_path=None):
    """Ranked scan records, or None when the artifact is absent/unreadable."""
    path = Path(scan_path) if scan_path else SCAN_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, list) else None


def _remote_json(rel_path, base, timeout=REMOTE_TIMEOUT):
    """Fetch one committed artifact from GitHub raw. None on any failure."""
    if not base:
        return None
    import urllib.request
    url = f"{base.rstrip('/')}/{rel_path.lstrip('/')}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except Exception:
        return None


def _remote_evidence(base):
    """Latest committed decision/scan/vibe straight from GitHub, or None."""
    if not base:
        return None
    decision = _remote_json(REMOTE_DECISION, base)
    if not isinstance(decision, dict):
        return None
    scan = _remote_json(REMOTE_SCAN, base)
    vibe = _remote_json(REMOTE_VIBE, base)
    return {
        "decision": decision,
        "scan": scan if isinstance(scan, list) else None,
        "vibe": vibe if isinstance(vibe, dict) else None,
    }


def _pair_candidates(symbol):
    """Possible decision/scan keys for a webhook symbol ('BTC', 'BTCUSDT', 'BTC/USDT')."""
    raw = str(symbol).upper().strip()
    base = re.split(r"[/\-_]", raw)[0]
    for quote in ("USDT", "USD", "USDC", "PERP"):
        if base.endswith(quote) and len(base) > len(quote):
            base = base[: -len(quote)]
            break
    ordered = [raw, f"{base}/USDT", f"{base}/USD", base]
    return tuple(dict.fromkeys(ordered))


def _decision_pairs(record):
    pairs = (record or {}).get("decision", {}).get("pairs")
    if not isinstance(pairs, dict):
        pairs = (record or {}).get("pairs")
    return pairs if isinstance(pairs, dict) else {}


def check_vibe(vibe_dir=None, now=None):
    """Freshness/presence check for the alpha-bench artifact alone."""
    reasons = []
    evidence = {}
    if not REQUIRE_VIBE:
        return {"allowed": True, "reasons": [], "evidence": evidence}
    try:
        from . import vibe_evidence
        path = vibe_evidence.latest_report(vibe_dir) if vibe_dir else vibe_evidence.latest_report()
        summary = vibe_evidence.summarize(path) if path else None
    except Exception:  # pragma: no cover - defensive only
        summary = None
    if not summary or not summary.get("top"):
        return {
            "allowed": False,
            "reasons": ["no Vibe-Trading alpha evidence artifact - fail closed"],
            "evidence": evidence,
        }
    vibe_age = summary.get("age_hours")
    best = summary["top"][0]
    evidence["vibe"] = {
        "artifact": summary.get("artifact"),
        "age_hours": vibe_age,
        "best_alpha": best.get("alpha"),
        "best_ir": best.get("ir"),
        "best_ic_mean": best.get("ic_mean"),
    }
    if vibe_age is not None and vibe_age > MAX_VIBE_AGE_H:
        reasons.append(f"stale alpha evidence: {vibe_age}h old (> {MAX_VIBE_AGE_H:g}h)")
    return {"allowed": not reasons, "reasons": reasons, "evidence": evidence}


def check_entry(symbol, decisions_dir=None, scan_path=None, vibe_dir=None, now=None,
                remote_base=None):
    """Decide whether a new entry for ``symbol`` may proceed.

    Returns {"allowed": bool, "reasons": [str], "evidence": {...}}.
    A missing or stale input blocks: this gate never guesses.
    """
    reasons = []
    evidence = {}
    now = now or datetime.now(timezone.utc)

    base = REMOTE_BASE if remote_base is None else str(remote_base).strip()
    remote = _remote_evidence(base) if base else None
    path = None
    if remote:
        record = remote["decision"]
        evidence["source"] = "github-raw"
    else:
        record, path = newest_decision(decisions_dir)
        evidence["source"] = "local"
        if record is None:
            return {
                "allowed": False,
                "reasons": ["no deliberation decision record - fail closed"],
                "evidence": evidence,
            }

    generated = record.get("generated_at") or record.get("asof")
    age = _age_hours(generated, now)
    evidence["decision"] = {
        "path": path.as_posix() if path else f"{base.rstrip('/')}/{REMOTE_DECISION}",
        "generated_at": generated,
        "age_hours": age,
    }
    if age is None:
        reasons.append("decision has no usable timestamp - fail closed")
    elif age > MAX_DECISION_AGE_H:
        reasons.append(
            f"stale decision: {age}h old (> {MAX_DECISION_AGE_H:g}h) - "
            "wait for the next deliberation cycle"
        )

    if REQUIRE_VIBE:
        if remote and remote.get("vibe"):
            summary = remote["vibe"]
            vibe_age = _age_hours(summary.get("generated_at"), now)
            if summary.get("age_hours") is not None:
                vibe_age = summary["age_hours"]
            top = summary.get("top") or []
            if not top:
                reasons.append("no Vibe-Trading alpha evidence artifact - fail closed")
                evidence["vibe"] = None
            else:
                best = top[0]
                evidence["vibe"] = {
                    "artifact": summary.get("artifact"),
                    "age_hours": vibe_age,
                    "best_alpha": best.get("alpha"),
                    "best_ir": best.get("ir"),
                    "best_ic_mean": best.get("ic_mean"),
                }
                if vibe_age is not None and vibe_age > MAX_VIBE_AGE_H:
                    reasons.append(
                        f"stale alpha evidence: {vibe_age}h old (> {MAX_VIBE_AGE_H:g}h)"
                    )
        else:
            vibe = check_vibe(vibe_dir=vibe_dir, now=now)
            reasons.extend(vibe["reasons"])
            evidence["vibe"] = vibe["evidence"].get("vibe")

    scan = remote["scan"] if remote else None
    if not isinstance(scan, list):
        scan = load_asset_scan(scan_path)
    if scan is not None:
        keys = {str(item.get("pair", "")).upper() for item in scan if isinstance(item, dict)}
        match = None
        for candidate in _pair_candidates(symbol):
            if str(candidate).upper() in keys:
                match = str(candidate).upper()
                break
        row = next(
            (i for i in scan
             if isinstance(i, dict) and str(i.get("pair", "")).upper() == match),
            None,
        )
        if row is not None:
            score = row.get("profit_score")
            evidence["scan"] = {"pair": row.get("pair"), "profit_score": score}
            if REQUIRE_POSITIVE_SCAN and isinstance(score, (int, float)) and score < 0:
                reasons.append(
                    f"asset scan ranks {row.get('pair')} at {score} (<0) - "
                    "no positive edge signal"
                )
        else:
            evidence["scan"] = {"pair": None, "reason": "symbol not in scanned universe"}

    pairs = _decision_pairs(record)
    entry = None
    for candidate in _pair_candidates(symbol):
        if candidate in pairs:
            entry = pairs[candidate]
            break
    if entry is None:
        reasons.append(f"{symbol} not in deliberation decision - fail closed")
    else:
        evidence["decision_pair"] = entry

    return {"allowed": not reasons, "reasons": reasons, "evidence": evidence}


def main(argv=None):
    """CLI: exit 0 when an entry would be allowed, 1 when evidence blocks it."""
    import argparse

    parser = argparse.ArgumentParser(prog="python -m agents.evidence_gate")
    parser.add_argument("--symbol", required=True, help="e.g. BTC or BTCUSDT or BTC/USDT")
    parser.add_argument("--remote-base", default=None,
                        help="override TB_EVIDENCE_REMOTE (GitHub raw base URL)")
    args = parser.parse_args(argv)
    result = check_entry(args.symbol, remote_base=args.remote_base)
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

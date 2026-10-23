#!/usr/bin/env python3
"""System check: are all reports, configs and the gate loaded and usable?

Answers "are we clean and are the reports ready?" with evidence, not prose.
Every check prints PASS / WARN / FAIL, and the process exits non-zero if any
check FAILs, so a broken pipeline is visible in CI instead of silent.

Covers:
  artifacts   scan, shortlist, decisions, latest pointer, learning, lessons,
              data quality, alpha evidence, today's brief -- parsed + fresh
  configs     repo MCP config + Alphacode MCP configs contain vibe-trading
  gate        evidence gate runs for the symbols in the latest decision
  git         working tree clean and not behind origin (local runs only)

Usage:
    python scripts/system_check.py            # human table, exit 1 on FAIL
    python scripts/system_check.py --json     # machine-readable
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STATE = {"PASS": 0, "WARN": 0, "FAIL": 0}
RESULTS = []


def _add(name, status, detail):
    RESULTS.append({"check": name, "status": status, "detail": detail})
    STATE[status] = STATE.get(status, 0) + 1


def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return e


def _stamp_of(payload):
    if isinstance(payload, dict):
        for key in ("generated_at", "asof"):
            value = payload.get(key)
            if value:
                try:
                    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
                except ValueError:
                    pass
    return None


def _check_artifact(name, rel_path, expect=list, max_age_h=36.0, required=True, now=None):
    now = now or datetime.now(timezone.utc)
    path = ROOT / rel_path
    if not path.is_file():
        _add(name, "FAIL" if required else "WARN", f"missing: {rel_path}")
        return None
    payload = _load_json(path)
    if isinstance(payload, Exception):
        _add(name, "FAIL", f"unparseable JSON: {payload}")
        return None
    if expect is list and not isinstance(payload, list):
        _add(name, "FAIL", f"expected list, got {type(payload).__name__}")
        return None
    if expect is dict and not isinstance(payload, dict):
        _add(name, "FAIL", f"expected object, got {type(payload).__name__}")
        return None
    if expect is list and not payload:
        _add(name, "FAIL", "artifact is empty")
        return None

    stamp = _stamp_of(payload) or datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    age = round((now - stamp).total_seconds() / 3600.0, 1)
    if age > max_age_h:
        _add(name, "FAIL", f"stale {age}h (> {max_age_h:g}h) :: {rel_path}")
    else:
        size = path.stat().st_size
        _add(name, "PASS", f"{age}h old, {size} bytes :: {rel_path}")
    return payload


def check_artifacts(now=None):
    now = now or datetime.now(timezone.utc)
    scan = _check_artifact("scan", "research/reports/asset_scan.json", list, 26.0, now=now)
    if scan:
        classes = sorted({row.get("asset_class") for row in scan if isinstance(row, dict)})
        _add("scan classes", "PASS" if len(classes) >= 3 else "FAIL",
             f"{len(scan)} rows, classes={classes}")
    _check_artifact("shortlist", "research/reports/scan_shortlist.json", dict, 26.0, now=now)
    _check_artifact("learning", "research/reports/learning/daily_learning.json", dict, 36.0, now=now)
    _check_artifact("quality", "research/reports/quality/data_quality.json", dict, 36.0, now=now)
    _check_artifact("alpha evidence", "research/reports/vibe/latest.json", dict, 72.0, now=now)
    _check_artifact("latest decision", "user_data/decisions/latest.json", dict, 36.0, now=now)

    decisions = sorted((ROOT / "reports" / "decisions").glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not decisions:
        _add("decision record", "FAIL", "no reports/decisions/*.json")
    else:
        newest = decisions[-1]
        payload = _load_json(newest)
        if isinstance(payload, Exception):
            _add("decision record", "FAIL", f"unparseable: {newest.name}")
        else:
            pairs = ((payload.get("decision") or {}).get("pairs")
                     or payload.get("pairs") or {})
            _add("decision record", "PASS" if pairs else "FAIL",
                 f"{newest.name}: {len(pairs)} pairs")

    lessons = ROOT / "research" / "LESSONS_AUTO.md"
    if lessons.is_file() and lessons.stat().st_size > 0:
        _add("lessons", "PASS", f"{lessons.stat().st_size} bytes")
    else:
        _add("lessons", "FAIL", "research/LESSONS_AUTO.md missing/empty")

    briefs = sorted((ROOT / "research" / "reports" / "brief").glob("*.md"),
                    key=lambda p: p.stat().st_mtime)
    if not briefs:
        _add("brief", "FAIL", "no research/reports/brief/*.md")
    else:
        age = round((now - datetime.fromtimestamp(briefs[-1].stat().st_mtime, timezone.utc)).total_seconds() / 3600.0, 1)
        _add("brief", "PASS" if age <= 36 else "WARN", f"newest {briefs[-1].name} ({age}h)")


def check_configs():
    repo_mcp = ROOT / ".mcp.json"
    payload = _load_json(repo_mcp)
    if isinstance(payload, Exception):
        _add("repo .mcp.json", "FAIL", str(payload))
    else:
        ok = "vibe-trading" in (payload.get("mcpServers") or {})
        _add("repo .mcp.json", "PASS" if ok else "FAIL", "vibe-trading entry" if ok else "entry missing")

    home = Path(os.path.expanduser("~"))
    targets = [
        ("alphacode opencode.json", home / ".config" / "opencode" / "opencode.json", "mcp", "browseros"),
        ("alphacode mcp.json", home / ".alphacode" / "mcp.json", "servers", None),
    ]
    for name, path, key, extra in targets:
        if not path.is_file():
            _add(name, "WARN", "not present on this host (CI)")
            continue
        payload = _load_json(path)
        if isinstance(payload, Exception):
            _add(name, "FAIL", f"unparseable: {payload}")
            continue
        servers = payload.get(key) or {}
        ok = "vibe-trading" in servers
        _add(name, "PASS" if ok else "FAIL",
             "vibe-trading registered" if ok else f"vibe-trading missing from {key}")

    skill = home / ".alphacode" / "skills" / "trading-evidence-gate" / "SKILL.md"
    _add("trading skill", "PASS" if skill.is_file() else "WARN",
         "installed" if skill.is_file() else "not present on this host")


def check_gate():
    try:
        from agents import evidence_gate
    except Exception as e:
        _add("gate import", "FAIL", f"{type(e).__name__}: {e}")
        return
    record, _path = evidence_gate.newest_decision()
    pairs = list((evidence_gate._decision_pairs(record) or {}).keys())[:3]
    if not pairs:
        _add("gate run", "FAIL", "no decision pairs to check")
        return
    for pair in pairs:
        try:
            result = evidence_gate.check_entry(pair)
            item = (result.get("evidence", {}).get("decision_pair") or {})
            evidence_ok = "evidence ok" if result.get("allowed") else "evidence FAIL"
            detail = (f"{evidence_ok}; deliberation={item.get('action')} "
                      f"size={item.get('size')}")
            if result.get("reasons"):
                detail += f"; {'; '.join(result['reasons'])[:80]}"
            _add(f"gate {pair}", "PASS", detail)
        except Exception as e:
            _add(f"gate {pair}", "FAIL", f"{type(e).__name__}: {e}")


def check_git():
    try:
        status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        dirty = [line for line in status.stdout.splitlines() if line.strip()]
        _add("git tree", "PASS" if not dirty else "WARN", f"{len(dirty)} changed/untracked")
        counts = subprocess.run(["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        if counts.returncode == 0:
            behind, ahead = (counts.stdout.strip().split() + ["0", "0"])[:2]
            state = "PASS" if behind == "0" and ahead == "0" else "FAIL"
            _add("git sync", state, f"behind {behind}, ahead {ahead}")
    except Exception as e:
        _add("git", "WARN", f"unavailable ({type(e).__name__})")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scripts/system_check.py")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-git", action="store_true")
    args = parser.parse_args(argv)

    check_artifacts()
    check_configs()
    check_gate()
    if not args.no_git:
        check_git()

    if args.json:
        print(json.dumps({"counts": STATE, "results": RESULTS}, indent=2, default=str))
    else:
        print(f"SYSTEM CHECK  pass={STATE['PASS']} warn={STATE['WARN']} fail={STATE['FAIL']}")
        for row in RESULTS:
            print(f"[{row['status']:4s}] {row['check']:22s} {row['detail']}")
    return 0 if STATE["FAIL"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

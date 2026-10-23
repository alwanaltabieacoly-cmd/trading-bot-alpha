"""Cite Vibe-Trading alpha-benchmark evidence inside deliberation.

The CI job ``.github/workflows/vibe-research.yml`` commits a plain-text log per
run under ``research/reports/vibe/``. Each log ends with a JSON result block
(``status``, ``zoo``, ``universe``, ``period``, ``top`` ...), which this module
reduces to a small, citable summary. Missing or unparseable reports degrade to
``None``: deliberation must never fail because CI has not produced a benchmark.

Standalone use (used by the workflow summary step):

    python -m agents.vibe_evidence
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "research" / "reports" / "vibe"
MAX_ALPHAS = 5
_NAME_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})_\d+_(?P<zoo>[a-z0-9]+)_(?P<universe>[a-z0-9]+)$")


def _extract_json(text):
    """Return the first JSON object in text that looks like a bench result."""
    decoder = json.JSONDecoder()
    index = 0
    while True:
        start = text.find("{", index)
        if start == -1:
            return None
        try:
            obj, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(obj, dict) and ("status" in obj or "top" in obj):
            return obj
        index = start + 1


def latest_report(reports_dir=None):
    """Newest benchmark log, or None when none has been committed yet."""
    directory = Path(reports_dir) if reports_dir else REPORTS_DIR
    try:
        if not directory.is_dir():
            return None
        files = [p for p in directory.glob("*.txt") if p.is_file()]
        if not files:
            return None
        return max(files, key=lambda p: p.stat().st_mtime)
    except OSError:
        return None


def summarize(report_path=None, max_alphas=MAX_ALPHAS):
    """Reduce the newest (or given) benchmark log to a citable dict."""
    path = Path(report_path) if report_path else latest_report()
    if path is None or not path.is_file():
        return None

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    data = _extract_json(text)
    if not data or data.get("status") != "ok":
        return None

    top = []
    for row in (data.get("top") or [])[:max_alphas]:
        if not isinstance(row, dict):
            continue
        theme = row.get("theme")
        if isinstance(theme, list):
            theme = ",".join(str(t) for t in theme)
        top.append({
            "alpha": row.get("id"),
            "theme": theme or row.get("category"),
            "ic_mean": row.get("ic_mean"),
            "ir": row.get("ir"),
            "ic_positive_ratio": row.get("ic_positive_ratio"),
            "ic_count": row.get("ic_count"),
        })
    if not top:
        return None

    match = _NAME_RE.match(path.stem)
    try:
        stat = path.stat()
        age_hours = round((__import__("time").time() - stat.st_mtime) / 3600.0, 2)
        generated_at = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
    except OSError:
        age_hours, generated_at = None, None
    return {
        "source": "vibe-trading alpha_bench",
        "artifact": path.as_posix(),
        "age_hours": age_hours,
        "generated_at": generated_at,
        "asof": match.group("date") if match else None,
        "zoo": data.get("zoo"),
        "universe": data.get("universe"),
        "period": data.get("period"),
        "n_alphas_tested": data.get("n_alphas_tested"),
        "n_skipped": data.get("n_skipped"),
        "top": top,
        "caveats": [
            "cross-sectional IC across the universe, not a per-pair entry signal",
            "constituents are the current list (survivorship-biased) -> IC quoted above is biased upward",
        ],
    }


def blackboard_entry(summary):
    """Turn a summary into a schema-valid Blackboard entry (or None)."""
    if not summary or not summary.get("top"):
        return None
    best = summary["top"][0]
    others = ", ".join(
        f"{row['alpha']} (IR {row['ir']})" for row in summary["top"][1:4]
    )
    text = (
        f"Vibe-Trading alpha bench {summary.get('zoo')} / {summary.get('universe')} "
        f"{summary.get('period')}: best factor {best['alpha']} "
        f"IR={best['ir']} IC_mean={best['ic_mean']} N={best['ic_count']}"
    )
    if others:
        text += f"; next: {others}"
    return {
        "agent": "vibe-factors",
        "round": 1,
        "claims": [{
            "text": text,
            "evidence": [
                f"artifact={summary['artifact']}",
                f"n_alphas_tested={summary.get('n_alphas_tested')}",
                f"best_alpha={best['alpha']} ir={best['ir']} ic_mean={best['ic_mean']}",
                f"caveat={summary['caveats'][0]}",
            ],
        }],
        "recommendation": "abstain",
        "confidence": 0.5,
        "blockers": [],
        "pair_recommendations": {},
    }


def summary_text(summary):
    """Human-readable block for the GitHub step summary."""
    if not summary:
        return "no Vibe-Trading benchmark artifact found (run the 'Vibe-Trading research' workflow first)"
    lines = [
        f"Vibe-Trading `{summary.get('zoo')}` on `{summary.get('universe')}` "
        f"({summary.get('period')}): {summary.get('n_alphas_tested')} tested, "
        f"{summary.get('n_skipped')} skipped",
        "",
        "| # | alpha | theme | IC mean | IR | IC+ ratio | N |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, row in enumerate(summary["top"], 1):
        lines.append(
            f"| {i} | {row['alpha']} | {row['theme']} | {row['ic_mean']} | "
            f"{row['ir']} | {row['ic_positive_ratio']} | {row['ic_count']} |"
        )
    lines += ["", f"artifact: `{summary['artifact']}`", ""]
    lines += [f"- caveat: {c}" for c in summary["caveats"]]
    return "\n".join(lines)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(prog="python -m agents.vibe_evidence")
    parser.add_argument("--json", action="store_true",
                        help="emit the summary as JSON (used by the workflow pointer file)")
    args = parser.parse_args(argv)
    summary = summarize()
    if args.json:
        print(json.dumps(summary or {}, indent=2, default=str))
    else:
        print(summary_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

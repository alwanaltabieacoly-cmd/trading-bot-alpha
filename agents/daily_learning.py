"""Daily learning digest: turn labelled outcomes into rules the agent must read.

Sources
-------
Every warmup verdict is later labelled CORRECT / MISSED / WRONG and appended to
``research/reports/warmup/outcome_log.jsonl`` (batch rows: ``{"ts", "outcomes": [...]}``)
and/or ``research/reports/verdicts/outcome_log.jsonl`` (flat rows). Both shapes
are accepted; malformed lines are skipped, never fatal.

Outputs
-------
* ``research/reports/learning/daily_learning.json``  - metrics + lessons (machine)
* ``research/LESSONS_AUTO.md``                       - append-only dated lessons (human/agent)
* ``prompt_block()``                                 - compact text injected into the
                                                       analyst prompt and deliberation

Design rule: this module reports what the data shows and says "insufficient
data" when it does not know. It never invents a lesson from a tiny sample.

Usage:
    python -m agents.daily_learning            # print metrics JSON
    python -m agents.daily_learning --write    # also write the artifacts
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_PATHS = (
    PROJECT_ROOT / "research" / "reports" / "warmup" / "outcome_log.jsonl",
    PROJECT_ROOT / "research" / "reports" / "verdicts" / "outcome_log.jsonl",
)
LEARNING_JSON = PROJECT_ROOT / "research" / "reports" / "learning" / "daily_learning.json"
LESSONS_MD = PROJECT_ROOT / "research" / "LESSONS_AUTO.md"

MIN_SAMPLES = 20          # below this, no statistical claims
MIN_PER_GROUP = 8         # below this, no per-pair / per-verdict claims
TREND_DAYS = 7
MAX_LESSONS = 6
LESSONS_TAIL_LINES = 400  # keep the append-only file bounded


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------
def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def load_outcomes(log_paths=None):
    """Return normalized outcome rows: ts, pair, verdict, change_pct, result, score."""
    rows = []
    for path in (log_paths or LOG_PATHS):
        path = Path(path)
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            ts = rec.get("ts")
            if isinstance(rec.get("outcomes"), list):
                for item in rec["outcomes"]:
                    if not isinstance(item, dict):
                        continue
                    change = item.get("price_change_pct")
                    if change is None:
                        change = item.get("price_change_1h_pct", item.get("price_change_1d_pct"))
                    rows.append({
                        "ts": ts,
                        "pair": item.get("pair"),
                        "verdict": item.get("verdict"),
                        "change_pct": change,
                        "result": item.get("result"),
                        "score": item.get("score"),
                    })
            elif rec.get("result"):
                rows.append({
                    "ts": ts,
                    "pair": rec.get("pair"),
                    "verdict": rec.get("verdict"),
                    "change_pct": rec.get("price_change_pct"),
                    "result": rec.get("result"),
                    "score": rec.get("score"),
                })
    for row in rows:
        dt = _parse_ts(row["ts"])
        row["_dt"] = dt
    return rows


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------
def _acc(rows):
    total = len(rows)
    hits = sum(1 for r in rows if str(r.get("result", "")).upper() == "CORRECT")
    misses = total - hits
    return {
        "n": total,
        "hits": hits,
        "misses": misses,
        "accuracy": round(hits / total, 3) if total else None,
    }


def _bucket(score):
    if score is None:
        return None
    score = float(score)
    for limit, label in ((-5, "<-5"), (-2, "-5..-2"), (0, "-2..0"),
                         (2, "0..2"), (5, "2..5")):
        if score < limit:
            return label
    return ">5"


def compute_metrics(records, now=None):
    """Aggregate accuracy overall, per verdict, per pair, per score bucket, trend."""
    now = now or datetime.now(timezone.utc)
    rows = [r for r in records if r.get("result")]
    overall = _acc(rows)

    by_verdict = {}
    for verdict in ("GO", "NO-GO"):
        group = [r for r in rows if str(r.get("verdict", "")).upper() == verdict]
        if group:
            by_verdict[verdict] = _acc(group)

    by_pair = {}
    for pair in sorted({r.get("pair") for r in rows if r.get("pair")}):
        group = [r for r in rows if r.get("pair") == pair]
        if group:
            by_pair[pair] = _acc(group)

    by_bucket = {}
    for label in ("<-5", "-5..-2", "-2..0", "0..2", "2..5", ">5"):
        group = [r for r in rows if _bucket(r.get("score")) == label]
        if group:
            by_bucket[label] = _acc(group)

    def _window(days_start, days_end):
        edge = now - timedelta(days=days_start)
        floor = now - timedelta(days=days_end)
        return [r for r in rows if r.get("_dt") and floor < r["_dt"] <= edge]

    recent = _acc(_window(TREND_DAYS, 0))
    previous = _acc(_window(TREND_DAYS * 2, TREND_DAYS))
    trend = {
        "recent": recent,
        "previous": previous,
        "delta": (
            round(recent["accuracy"] - previous["accuracy"], 3)
            if recent["accuracy"] is not None and previous["accuracy"] is not None
            else None
        ),
    }

    return {
        "generated_at": now.isoformat(),
        "overall": overall,
        "by_verdict": by_verdict,
        "by_pair": by_pair,
        "by_score_bucket": by_bucket,
        "trend_7d": trend,
        "sample_ok": overall["n"] >= MIN_SAMPLES,
    }


# ---------------------------------------------------------------------------
# lessons
# ---------------------------------------------------------------------------
def derive_lessons(metrics):
    """Deterministic, evidence-linked lessons. Empty list when data is thin."""
    lessons = []
    overall = metrics["overall"]

    if overall["n"] < MIN_SAMPLES:
        lessons.append({
            "id": "insufficient-data",
            "text": (
                f"Only {overall['n']} labelled outcomes (<{MIN_SAMPLES}) - treat every "
                "verdict as low confidence; do not increase size on this evidence."
            ),
            "evidence": f"n={overall['n']}",
        })
        return lessons

    for verdict, stats in metrics["by_verdict"].items():
        if stats["n"] < MIN_PER_GROUP:
            continue
        if stats["accuracy"] is not None and stats["accuracy"] < 0.40:
            lessons.append({
                "id": f"verdict-anti-{verdict.lower()}",
                "text": (
                    f"{verdict} verdicts are anti-predictive: {stats['accuracy']:.0%} "
                    f"accuracy over {stats['n']} labels. Do not treat a {verdict} as a "
                    "directional signal; require extra confirmation."
                ),
                "evidence": f"{verdict}: {stats['hits']}/{stats['n']} correct",
            })
        elif stats["accuracy"] is not None and stats["accuracy"] >= 0.60:
            lessons.append({
                "id": f"verdict-reliable-{verdict.lower()}",
                "text": (
                    f"{verdict} verdicts are historically reliable: "
                    f"{stats['accuracy']:.0%} over {stats['n']} labels. Honour them."
                ),
                "evidence": f"{verdict}: {stats['hits']}/{stats['n']} correct",
            })

    for pair, stats in metrics["by_pair"].items():
        if stats["n"] >= MIN_PER_GROUP and stats["accuracy"] is not None and stats["accuracy"] < 0.40:
            lessons.append({
                "id": f"pair-unreliable-{str(pair).lower().replace('/', '-')}",
                "text": (
                    f"{pair} verdict accuracy is {stats['accuracy']:.0%} over {stats['n']} "
                    "labels - exclude it from new entries until accuracy recovers."
                ),
                "evidence": f"{pair}: {stats['hits']}/{stats['n']} correct",
            })

    buckets = metrics["by_score_bucket"]
    ordered = [(label, buckets[label]) for label in ("<-5", "-5..-2", "-2..0", "0..2", "2..5", ">5")
               if label in buckets and buckets[label]["n"] >= 5]
    if len(ordered) >= 2:
        low = ordered[0][1]["accuracy"]
        high = ordered[-1][1]["accuracy"]
        if low is not None and high is not None and low > high + 0.15:
            lessons.append({
                "id": "score-not-monotone",
                "text": (
                    "The warmup score is not monotone with outcomes "
                    f"(low bucket {low:.0%} vs high bucket {high:.0%}). Treat the score as "
                    "ordinal only; do not size up on a high score."
                ),
                "evidence": f"low={low:.0%} high={high:.0%}",
            })

    trend = metrics["trend_7d"]
    if trend["delta"] is not None and abs(trend["delta"]) >= 0.10:
        direction = "improving" if trend["delta"] > 0 else "degrading"
        lessons.append({
            "id": "trend-shift",
            "text": (
                f"Accuracy is {direction} ({trend['previous']['accuracy']:.0%} -> "
                f"{trend['recent']['accuracy']:.0%} over 7 days). "
                + ("Keep the current weighting." if trend["delta"] > 0
                   else "Re-check recent verdicts before trusting the score.")
            ),
            "evidence": f"delta={trend['delta']:+.0%}",
        })

    return lessons[:MAX_LESSONS]


# ---------------------------------------------------------------------------
# rendering / persistence
# ---------------------------------------------------------------------------
def learn(log_paths=None, now=None):
    records = load_outcomes(log_paths)
    metrics = compute_metrics(records, now=now)
    metrics["lessons"] = derive_lessons(metrics)
    return metrics


def prompt_block(metrics=None):
    """Compact text for the analyst prompt / blackboard ('' when no lessons)."""
    metrics = metrics or learn()
    lessons = metrics.get("lessons") or []
    if not lessons:
        return ""
    overall = metrics["overall"]
    head = (
        f"HISTORICAL LESSONS (from {overall['n']} labelled outcomes, "
        f"accuracy {overall['accuracy']:.0%}):"
    )
    bullets = " ".join(f"({i}) {item['text']}" for i, item in enumerate(lessons, 1))
    return head + " " + bullets + " Do not contradict these without new labelled evidence."


def markdown(metrics):
    overall = metrics["overall"]
    lines = [f"# Daily learning - {metrics['generated_at'][:10]}", ""]
    lines.append(f"- labelled outcomes: **{overall['n']}**")
    if overall["accuracy"] is not None:
        lines.append(f"- accuracy: **{overall['accuracy']:.0%}** "
                     f"({overall['hits']}/{overall['n']})")
    lines.append("")
    if metrics["lessons"]:
        lines.append("## Lessons")
        lines += [f"- **{item['id']}**: {item['text']}  \n  _evidence: {item['evidence']}_"
                  for item in metrics["lessons"]]
    else:
        lines.append("No lessons: sample too thin or no failure pattern detected.")
    return "\n".join(lines) + "\n"


def write_artifacts(metrics=None, learning_json=None, lessons_md=None):
    """Persist the JSON digest and append deduped lessons to LESSONS_AUTO.md."""
    metrics = metrics or learn()
    learning_json = Path(learning_json or LEARNING_JSON)
    lessons_md = Path(lessons_md or LESSONS_MD)

    learning_json.parent.mkdir(parents=True, exist_ok=True)
    learning_json.write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")

    lessons_md.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if lessons_md.is_file():
        existing = lessons_md.read_text(encoding="utf-8", errors="replace")
    if not existing.strip():
        existing = ("# LESSONS_AUTO - generated daily from labelled outcomes\n"
                    "<!-- Append-only. Written by agents/daily_learning.py. -->\n")
    today = metrics["generated_at"][:10]
    block = [f"\n## {today}"]
    if not metrics["lessons"]:
        block.append("- no lessons (insufficient data or no failure pattern)")
    for item in metrics["lessons"]:
        line = f"- [{item['id']}] {item['text']} (evidence: {item['evidence']})"
        if line not in existing:  # idempotent: never duplicate a lesson
            block.append(line)
    if len(block) > 1:
        existing = existing.rstrip() + "\n" + "\n".join(block) + "\n"
    trimmed = existing.splitlines()[-LESSONS_TAIL_LINES:]
    lessons_md.write_text("\n".join(trimmed) + "\n", encoding="utf-8")
    return learning_json, lessons_md


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(prog="python -m agents.daily_learning")
    parser.add_argument("--write", action="store_true", help="write daily_learning.json + LESSONS_AUTO.md")
    parser.add_argument("--markdown", action="store_true", help="print a markdown digest instead of JSON")
    parser.add_argument("--json", action="store_true", help="print raw JSON (default)")
    args = parser.parse_args(argv)
    metrics = learn()
    if args.write:
        learning_json, lessons_md = write_artifacts(metrics)
        print(f"wrote {learning_json}")
        print(f"wrote {lessons_md}")
    if args.markdown:
        print(markdown(metrics))
    else:
        print(json.dumps(metrics, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agents import daily_learning


def _rows(count, result, pair="BTC/USDT", verdict="GO", score=1.0, start_hours_ago=1):
    base = datetime.now(timezone.utc)
    out = []
    for i in range(count):
        out.append({
            "ts": (base - timedelta(hours=start_hours_ago + i)).isoformat(),
            "pair": pair,
            "verdict": verdict,
            "price_change_pct": 0.1 if result == "CORRECT" else -0.1,
            "result": result,
            "score": score,
        })
    return out


class DailyLearningTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.logs = self.dir / "logs"
        self.logs.mkdir()

    def _log(self, rows, name="outcome_log.jsonl", batch=False):
        path = self.logs / name
        if batch:
            path.write_text(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                                        "outcomes": rows}) + "\n", encoding="utf-8")
        else:
            path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return [path]

    # ---- parsing --------------------------------------------------------
    def test_parses_flat_and_batch_shapes(self):
        flat = self._log(_rows(3, "CORRECT"), name="flat.jsonl")
        batch = self._log(_rows(2, "MISSED"), name="batch.jsonl", batch=True)
        records = daily_learning.load_outcomes(flat + batch)
        self.assertEqual(len(records), 5)
        self.assertEqual(sum(1 for r in records if r["result"] == "CORRECT"), 3)

    def test_malformed_lines_are_skipped(self):
        path = self.logs / "bad.jsonl"
        path.write_text("not json\n" + json.dumps(_rows(2, "CORRECT")[0]) + "\n", encoding="utf-8")
        records = daily_learning.load_outcomes([path])
        self.assertEqual(len(records), 1)

    # ---- metrics --------------------------------------------------------
    def test_accuracy_math(self):
        logs = self._log(_rows(2, "CORRECT") + _rows(2, "MISSED"))
        metrics = daily_learning.compute_metrics(daily_learning.load_outcomes(logs))
        self.assertEqual(metrics["overall"]["n"], 4)
        self.assertAlmostEqual(metrics["overall"]["accuracy"], 0.5)

    def test_insufficient_data_lesson_and_no_false_claims(self):
        logs = self._log(_rows(5, "MISSED"))
        metrics = daily_learning.learn(log_paths=logs)
        self.assertFalse(metrics["sample_ok"])
        self.assertEqual([item["id"] for item in metrics["lessons"]], ["insufficient-data"])
        self.assertIn("low confidence", daily_learning.prompt_block(metrics))

    def test_anti_predictive_verdict_lesson(self):
        logs = self._log(_rows(2, "CORRECT") + _rows(18, "MISSED"))
        metrics = daily_learning.learn(log_paths=logs)
        ids = {item["id"] for item in metrics["lessons"]}
        self.assertIn("verdict-anti-go", ids)

    def test_unreliable_pair_lesson(self):
        logs = self._log(
            _rows(2, "CORRECT", pair="ADA/USDT") + _rows(8, "MISSED", pair="ADA/USDT")
            + _rows(12, "CORRECT", pair="BTC/USDT")
        )
        metrics = daily_learning.learn(log_paths=logs)
        ids = {item["id"] for item in metrics["lessons"]}
        self.assertIn("pair-unreliable-ada-usdt", ids)

    def test_healthy_sample_yields_no_lessons(self):
        logs = self._log(_rows(10, "CORRECT") + _rows(10, "MISSED"))
        metrics = daily_learning.learn(log_paths=logs)
        self.assertEqual(metrics["lessons"], [])
        self.assertEqual(daily_learning.prompt_block(metrics), "")

    # ---- artifacts ------------------------------------------------------
    def test_write_artifacts_is_idempotent(self):
        logs = self._log(_rows(2, "CORRECT") + _rows(18, "MISSED"))
        metrics = daily_learning.learn(log_paths=logs)
        out_json = self.dir / "learning.json"
        out_md = self.dir / "LESSONS_AUTO.md"
        daily_learning.write_artifacts(metrics, learning_json=out_json, lessons_md=out_md)
        first = out_md.read_text(encoding="utf-8")
        daily_learning.write_artifacts(metrics, learning_json=out_json, lessons_md=out_md)
        second = out_md.read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertIn("verdict-anti-go", second)
        self.assertTrue(json.loads(out_json.read_text(encoding="utf-8"))["lessons"])

    def test_markdown_reports_accuracy_and_lessons(self):
        logs = self._log(_rows(2, "CORRECT") + _rows(18, "MISSED"))
        metrics = daily_learning.learn(log_paths=logs)
        md = daily_learning.markdown(metrics)
        self.assertIn("accuracy", md)
        self.assertIn("verdict-anti-go", md)


if __name__ == "__main__":
    sys.exit(unittest.main())

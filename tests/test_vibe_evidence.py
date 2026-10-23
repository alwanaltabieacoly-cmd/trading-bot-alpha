import sys
import unittest

from agents import blackboard, vibe_evidence

SAMPLE = """SP500 universe uses current constituents (wikipedia) -> survivorship-biased
✓ Bench complete. 2 tested, 1 skipped. Report:
/tmp/reports/alpha_bench_20261023T172900Z.html
{
  "status": "ok",
  "zoo": "academic",
  "universe": "sp500",
  "period": "2024-2025",
  "n_alphas_tested": 2,
  "n_skipped": 1,
  "top": [
    {
      "id": "academic_carhart_mom",
      "theme": ["momentum"],
      "ic_mean": 0.028392,
      "ir": 0.1217,
      "ic_positive_ratio": 0.5944,
      "ic_count": 249
    },
    {
      "id": "academic_strev",
      "theme": ["reversal"],
      "ic_mean": 0.011185,
      "ir": 0.0584,
      "ic_positive_ratio": 0.5062,
      "ic_count": 480
    }
  ]
}
"""


class TestVibeEvidence(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path

        self.dir = Path(tempfile.mkdtemp())

    def _write(self, text, name="2026-10-23_1722_academic_sp500.txt"):
        from pathlib import Path

        path = Path(self.dir) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_parses_committed_log(self):
        summary = vibe_evidence.summarize(self._write(SAMPLE))
        self.assertIsNotNone(summary)
        self.assertEqual(summary["zoo"], "academic")
        self.assertEqual(summary["universe"], "sp500")
        self.assertEqual(summary["n_alphas_tested"], 2)
        self.assertEqual(len(summary["top"]), 2)
        self.assertEqual(summary["top"][0]["alpha"], "academic_carhart_mom")
        self.assertEqual(summary["top"][0]["theme"], "momentum")
        self.assertEqual(summary["asof"], "2026-10-23")

    def test_missing_file_returns_none(self):
        self.assertIsNone(vibe_evidence.summarize(self.dir / "nope.txt"))

    def test_empty_directory_returns_none(self):
        self.assertIsNone(vibe_evidence.latest_report(self.dir))

    def test_error_status_returns_none(self):
        path = self._write('{"status": "error", "error": "universe load failed"}')
        self.assertIsNone(vibe_evidence.summarize(path))

    def test_garbage_log_returns_none(self):
        self.assertIsNone(vibe_evidence.summarize(self._write("no json here at all")))

    def test_blackboard_entry_passes_schema(self):
        entry = vibe_evidence.blackboard_entry(vibe_evidence.summarize(self._write(SAMPLE)))
        self.assertIsNotNone(entry)
        blackboard._validate_entry(entry)  # raises BlackboardError when invalid
        self.assertEqual(entry["agent"], "vibe-factors")
        self.assertEqual(entry["recommendation"], "abstain")

    def test_blackboard_entry_none_without_summary(self):
        self.assertIsNone(vibe_evidence.blackboard_entry(None))

    def test_summary_text_mentions_alpha_and_caveats(self):
        text = vibe_evidence.summary_text(vibe_evidence.summarize(self._write(SAMPLE)))
        self.assertIn("academic_carhart_mom", text)
        self.assertIn("survivorship", text)


if __name__ == "__main__":
    sys.exit(unittest.main())

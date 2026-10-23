import random
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import scan_ic  # noqa: E402


def _snapshots(sign=1.0, n=25, symbols=8):
    """Synthetic snapshots whose rank correlation has the requested sign."""
    out = []
    for t in range(n):
        scores, forwards = {}, {}
        rng = random.Random(1000 + t)
        for i, symbol in enumerate([f"S{i}" for i in range(symbols)]):
            scores[symbol] = float(i)
            # jitter large enough to occasionally invert neighbour ranks, so
            # IC varies across snapshots and IR is defined.
            forwards[symbol] = sign * (i / symbols) + 0.15 * (rng.random() - 0.5)
        out.append((f"2026-01-{t+1:02d}", scores, forwards))
    return out


class SpearmanTest(unittest.TestCase):
    def test_perfect_positive(self):
        self.assertAlmostEqual(scan_ic.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0, places=9)

    def test_perfect_negative(self):
        self.assertAlmostEqual(scan_ic.spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0, places=9)

    def test_constant_is_undefined(self):
        self.assertIsNone(scan_ic.spearman([1, 1, 1], [1, 2, 3]))

    def test_too_short_is_undefined(self):
        self.assertIsNone(scan_ic.spearman([1, 2], [1, 2]))


class AnalyseVerdictTest(unittest.TestCase):
    def _run(self, snapshots, class_name="crypto"):
        fake_data = {f"S{i}": None for i in range(8)}
        with mock.patch.object(scan_ic, "snapshots", return_value=snapshots):
            return scan_ic.analyse(class_name, data=fake_data)

    def test_predictive_when_ic_is_strong(self):
        result = self._run(_snapshots(sign=1.0))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["verdict"], "predictive", result)
        self.assertGreater(result["ic_mean"], 0.5)
        self.assertGreater(result["ir"], 0.15)

    def test_no_evidence_when_ic_is_negative(self):
        result = self._run(_snapshots(sign=-1.0))
        self.assertEqual(result["verdict"], "no-evidence", result)
        self.assertLess(result["ic_mean"], 0)

    def test_insufficient_without_snapshots(self):
        result = self._run([])
        self.assertEqual(result["status"], "insufficient")

    def test_markdown_reports_verdict(self):
        report = {"generated_at": "2026-10-23T00:00:00+00:00",
                  "classes": {"crypto": self._run(_snapshots(1.0))}}
        text = scan_ic.markdown(report)
        self.assertIn("predictive", text)
        self.assertIn("IC mean", text)


if __name__ == "__main__":
    sys.exit(unittest.main())

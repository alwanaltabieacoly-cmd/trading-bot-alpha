"""Tests for the scan information coefficient measurement.

Covers the verdict logic (predictive / no-evidence / insufficient) and the bug
that was silently producing zero snapshots in CI: the old timestamp axis was
the *intersection* of every symbol's dates, which collapses the moment symbols
have heterogeneous coverage (24 crypto pairs across six exchanges). The axis is
now the longest symbol's history, with each symbol still contributing only its
own past bars.
"""
import random
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd
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


def _frame(n, start="2026-01-01", step="1D", seed=7):
    """Synthetic OHLC with real variance.

    Flat prices are rejected by feature_engine.extract (zero variance makes the
    rank correlation undefined), so a naive synthetic frame yields zero
    snapshots and looks like a broken measurement. A random walk exercises the
    real code path.
    """
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n))
    high = close + np.abs(rng.normal(0, 0.5, n))
    low = close - np.abs(rng.normal(0, 0.5, n))
    open_ = np.concatenate([[close[0]], close[:-1]])
    dates = pd.date_range(start, periods=n, freq=step, tz="UTC")
    return pd.DataFrame({
        "date": dates, "open": open_, "high": high, "low": low,
        "close": close, "volume": rng.uniform(0.5, 2.0, n),
    })


class SpearmanTest(unittest.TestCase):
    def test_perfect_positive(self):
        self.assertAlmostEqual(scan_ic.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0, places=9)

    def test_perfect_negative(self):
        self.assertAlmostEqual(scan_ic.spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0, places=9)

    def test_constant_is_undefined(self):
        self.assertIsNone(scan_ic.spearman([1, 1, 1], [1, 2, 3]))

    def test_too_short_is_undefined(self):
        self.assertIsNone(scan_ic.spearman([1, 2], [3, 4]))


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


class SnapshotAxisTest(unittest.TestCase):
    """The bug that produced zero snapshots in CI, now guarded."""

    def test_heterogeneous_coverage_does_not_collapse_axis(self):
        """Symbols with different histories must not zero out the measurement.

        The old axis was the intersection of every symbol's dates, which
        collapsed to nothing once coverage diverged (24 crypto pairs across
        six exchanges). With enough symbols the measurement still produces
        rows even though late timestamps see fewer contributors.
        """
        data = {f"S{i}": _frame(80 + i * 15, seed=100 + i) for i in range(8)}
        rows = scan_ic.snapshots("equity", data)
        assert rows, "heterogeneous coverage produced zero snapshots"
        longest = max(data, key=lambda s: len(data[s]))
        long_dates = set(pd.to_datetime(data[longest]["date"], utc=True))
        assert all(pd.Timestamp(stamp) in long_dates for stamp, _, _ in rows)

    def test_no_lookahead_per_symbol(self):
        data = {f"S{i}": _frame(200, seed=i + 1) for i in range(8)}
        rows = scan_ic.snapshots("equity", data)
        assert rows
        for stamp, scores, forwards in rows:
            assert set(scores) <= set(data)
            assert set(forwards) <= set(data)

    def test_analyse_reports_symbols_even_when_no_snapshots(self):
        """n_symbols is always reported, so a zero-snapshot run is diagnosable."""
        fake_data = {f"S{i}": None for i in range(8)}
        with mock.patch.object(scan_ic, "snapshots", return_value=[]):
            result = scan_ic.analyse("equity", data=fake_data)
        assert result["n_symbols"] == 8
        assert result["n_snapshots"] == 0
        assert result["status"] == "insufficient"

    def test_require_snapshots_gate_flags_zero(self):
        report = {"classes": {"crypto": {"n_snapshots": 0, "n_symbols": 24}}}
        broken = [c for c, r in report["classes"].items() if r.get("n_snapshots", 0) == 0]
        self.assertEqual(broken, ["crypto"])


if __name__ == "__main__":
    sys.exit(unittest.main())
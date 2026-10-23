import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import data_quality  # noqa: E402

NOW = datetime(2026, 10, 23, 20, 0, tzinfo=timezone.utc)


def _frame(days=120, bars_per_day=6, last_hours_ago=2, zero_volume=False):
    periods = int(days * bars_per_day)
    end = NOW - timedelta(hours=last_hours_ago)
    dates = pd.date_range(end=end, periods=periods, freq=f"{int(24 * 60 / bars_per_day)}min", tz="UTC")
    close = pd.Series(np.linspace(100, 120, periods))
    return pd.DataFrame({
        "date": dates,
        "open": close, "high": close + 1, "low": close - 1, "close": close,
        "volume": 0.0 if zero_volume else 1000.0,
    })


class DataQualityTest(unittest.TestCase):
    def _audit_with(self, frame, asset_class="crypto"):
        with mock.patch.object(data_quality, "_load_frame", return_value=frame):
            return data_quality._audit_symbol("BTC" if asset_class == "crypto" else "AAPL",
                                              asset_class, NOW)

    def test_healthy_crypto_is_ok(self):
        row = self._audit_with(_frame())
        self.assertEqual(row["verdict"], "ok", row)
        self.assertGreater(row["bars"], 300)
        self.assertLess(row["gap_ratio"], 0.15)

    def test_missing_data_is_bad(self):
        row = self._audit_with(None)
        self.assertEqual(row["verdict"], "bad")
        self.assertIn("no cached data", row["reason"])

    def test_large_gaps_are_bad(self):
        sparse = _frame(days=120, bars_per_day=1)  # 1 bar per day vs 6 expected
        row = self._audit_with(sparse)
        self.assertEqual(row["verdict"], "bad")
        self.assertIn("gap ratio", row["reason"])

    def test_stale_crypto_is_reported(self):
        row = self._audit_with(_frame(last_hours_ago=48))
        self.assertIn("stale", row["reason"])

    def test_zero_volume_warns_outside_forex(self):
        row = self._audit_with(_frame(zero_volume=True), asset_class="equity")
        self.assertIn("zero-volume", row["reason"])

    def test_forex_zero_volume_is_not_flagged(self):
        row = self._audit_with(_frame(zero_volume=True), asset_class="forex")
        self.assertNotIn("zero-volume", row["reason"])


class AuditAggregateTest(unittest.TestCase):
    def test_counts_and_markdown(self):
        with mock.patch.object(data_quality, "_load_frame", return_value=_frame()):
            report = data_quality.audit(limit=2, now=NOW)
        self.assertGreater(report["counts"]["ok"], 0)
        md = data_quality.markdown(report)
        self.assertIn("## Data quality", md)
        self.assertIn("ok **", md)
        self.assertIn("crypto:", md)


if __name__ == "__main__":
    sys.exit(unittest.main())

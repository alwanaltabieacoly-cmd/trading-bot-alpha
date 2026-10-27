import sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import check_staleness as cs

def stale_for(last_daily_text, now):
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "last_daily.txt").write_text(last_daily_text)
        with mock.patch.object(cs, "RULES", (("last_daily.txt", "Gate daily", 28.0),)), mock.patch.object(cs, "ROOT", Path(d)), \
             mock.patch.object(cs, "_state", return_value={}):
            return cs.detect(now)["workflows"]

class GateDailyWatch(unittest.TestCase):
    def test_missed_day_is_stale(self): self.assertEqual(stale_for("2026-10-26", datetime(2026, 10, 28, 4, 5, tzinfo=timezone.utc)), ["Gate daily"])
    def test_retry_window_is_not_stale(self): self.assertEqual(stale_for("2026-10-26", datetime(2026, 10, 27, 1, 30, tzinfo=timezone.utc)), [])
    def test_today_is_fine(self): self.assertEqual(stale_for("2026-10-27", datetime(2026, 10, 27, 20, 0, tzinfo=timezone.utc)), [])
    def test_real_rule_is_registered(self): self.assertIn(("research/gate_state/last_daily.txt", "Gate daily", 28.0), cs.RULES)

if __name__ == "__main__": unittest.main()

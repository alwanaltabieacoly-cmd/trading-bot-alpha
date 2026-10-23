"""Gate for the twice-daily deliberation schedule (unit tests)."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import should_run_deliberate as gate  # noqa: E402


def _at(hour, minute=0, day=23):
    return datetime(2026, 10, day, hour, minute, tzinfo=timezone.utc)


class DeliberateGateTest(unittest.TestCase):
    def test_force_always_runs(self):
        with mock.patch.object(gate, "newest_decision_time", return_value=_at(4, 0) - timedelta(minutes=5)):
            run, reason = gate.decide(now=_at(9), force=True)
        self.assertTrue(run)
        self.assertIn("forced", reason)

    def test_slot_hours_run(self):
        old = _at(4) - timedelta(hours=9)
        for hour in (4, 10):
            with mock.patch.object(gate, "newest_decision_time", return_value=old):
                run, reason = gate.decide(now=_at(hour, 5))
            self.assertTrue(run, (hour, reason))
            self.assertIn("slot hour", reason)

    def test_no_double_run_within_two_hours(self):
        last = _at(10, 5) - timedelta(minutes=20)
        with mock.patch.object(gate, "newest_decision_time", return_value=last):
            run, reason = gate.decide(now=_at(10, 30))
        self.assertFalse(run)
        self.assertIn("already ran", reason)

    def test_outside_slots_skips(self):
        old = _at(4) - timedelta(hours=4)
        with mock.patch.object(gate, "newest_decision_time", return_value=old):
            run, reason = gate.decide(now=_at(7, 15))
        self.assertFalse(run)
        self.assertIn("outside slots", reason)

    def test_catchup_after_20h(self):
        last = _at(4) - timedelta(hours=21)
        with mock.patch.object(gate, "newest_decision_time", return_value=last):
            run, reason = gate.decide(now=_at(18))
        self.assertTrue(run)
        self.assertIn("catch-up", reason)

    def test_missing_decision_runs(self):
        with mock.patch.object(gate, "newest_decision_time", return_value=None):
            run, reason = gate.decide(now=_at(7))
        self.assertTrue(run)
        self.assertIn("catch-up", reason)

    def test_writes_github_env(self):
        import tempfile

        env_path = Path(tempfile.mkdtemp()) / "env"
        env_path.write_text("", encoding="utf-8")
        with mock.patch.object(gate, "newest_decision_time", return_value=None):
            gate.decide(now=_at(7))
            gate.main(["--github-env", str(env_path)])
        content = env_path.read_text(encoding="utf-8")
        self.assertIn("RUN_NOW=1", content)
        self.assertIn("RUN_REASON=", content)


if __name__ == "__main__":
    sys.exit(unittest.main())

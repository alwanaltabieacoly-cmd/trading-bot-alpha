import sys, time, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "research"))
import gate_bot as b

def rows(setup, nets, base=0.0, start=0): return [{"tags": [setup], "day": start + i, "net": n, "base": base} for i, n in enumerate(nets)]
TODAY = time.strftime("%Y-%m-%d", time.gmtime()); NOW = int(time.time())

class AutoGate(unittest.TestCase):
    def test_no_evidence_is_blocked(self): self.assertEqual(b.setup_status("setup_x", [], [])[0], "blocked")
    def test_no_setup_is_blocked(self): self.assertEqual(b.setup_status(None, rows("a", [1]), [])[0], "blocked")
    def test_positive_backfill_explores_at_small_risk(self):
        s = b.setup_status("setup_x", rows("setup_x", [1, -0.5, 1]), [])
        self.assertEqual((s[0], s[1]), ("explore", b.EXPLORE_RISK_PCT))
    def test_negative_backfill_blocked(self): self.assertEqual(b.setup_status("setup_x", rows("setup_x", [-1, 0.2]), [])[0], "blocked")
    def test_live_outranks_backfill(self):   # backfill looks great, 10 live days lose: blocked
        self.assertEqual(b.setup_status("setup_x", rows("setup_x", [5] * 50), rows("setup_x", [-0.3] * 10))[0], "blocked")
    def test_calls_on_one_day_count_once(self):   # 40 correlated calls on a single day are one observation
        live = [{"tags": ["setup_x"], "day": 1, "net": 1.0, "base": 0.0} for _ in range(40)]
        self.assertEqual(b.setup_status("setup_x", rows("setup_x", [-1]), live)[0], "blocked")   # still using the backfill, which is negative
    def test_proven_needs_30_days_and_lower_bound(self):
        win = rows("setup_x", [1.0] * 30)
        self.assertEqual(b.setup_status("setup_x", [], win)[0], "proven")
        mixed = rows("setup_x", [1.0, -1.0] * 15, base=0.0)    # 50% wins: lower bound far under 50%
        self.assertEqual(b.setup_status("setup_x", [], mixed)[0], "blocked")   # mean 0, not positive
    def test_proven_must_beat_holding(self):
        self.assertNotEqual(b.setup_status("setup_x", [], rows("setup_x", [1.0] * 30, base=2.0))[0], "proven")

class Halts(unittest.TestCase):
    def closed(self, pnl, ts=NOW): return {"closed": ts, "pnl_usd": pnl}
    def test_within_limits(self): self.assertIsNone(b.check_halt([self.closed(-2)], 1000, 1000, TODAY))
    def test_daily_loss(self): self.assertIn("daily loss", b.check_halt([self.closed(-6), self.closed(-5)], 1000, 1000, TODAY))
    def test_yesterdays_loss_does_not_count(self): self.assertIsNone(b.check_halt([self.closed(-50, NOW - 2 * 86400)], 1000, 1000, TODAY))
    def test_open_trades_do_not_count(self): self.assertIsNone(b.check_halt([{"opened": NOW}], 1000, 1000, TODAY))
    def test_drawdown(self): self.assertIn("drawdown", b.check_halt([], 940, 1000, TODAY))
    def test_small_drawdown_ok(self): self.assertIsNone(b.check_halt([], 960, 1000, TODAY))
    def test_gain_never_halts(self): self.assertIsNone(b.check_halt([self.closed(30)], 1030, 1030, TODAY))

if __name__ == "__main__": unittest.main()

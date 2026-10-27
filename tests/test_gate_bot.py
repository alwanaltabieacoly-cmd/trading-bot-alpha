import json, sys, time, unittest
from unittest import mock
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

class AlphaTrade(unittest.TestCase):
    """Alpha trades through the bot's own halts and risk. Everything external is faked."""
    def setUp(self):
        import tempfile, gate_alpha as G
        self.d = Path(tempfile.mkdtemp()); self.G = G; self.saved = (b.LOG, b.HALT, b.EQUITY, b.T, b.G, b.equity_now)
        b.LOG, b.HALT, b.EQUITY = self.d / "trades.jsonl", self.d / "HALT.txt", self.d / "equity.json"
        self.made, self.opened = [], []
        class T:
            @staticmethod
            def open_trade(coin, side, stop, target, limits): outer.opened.append((coin, side, limits)); return {"fill_price": 1.0, "stop": 0.9, "target": 1.2, "contracts": 3, "risk_usd": 2.0, "notional": 30.0}
        outer = self; b.T = T
        class GG:
            @staticmethod
            def make_call(*a, **k): outer.made.append(a)
        b.G = GG; b.equity_now = lambda: (1000.0, 1000.0)
    def tearDown(self): b.LOG, b.HALT, b.EQUITY, b.T, b.G, b.equity_now = self.saved
    def test_opens_at_explore_risk_after_logging_the_call(self):
        r = b.alpha_trade("ETH_USDT", "long", 2.0, 4.0, "reclaimed the low")
        self.assertEqual(self.made[0][:3], ("ETH_USDT", "long", 2.0)); self.assertEqual(self.opened, [("ETH_USDT", "long", {"risk_pct": b.EXPLORE_RISK_PCT})])
        self.assertEqual((r["setup"], r["coin"]), ("alpha", "ETH_USDT")); self.assertEqual(len(b.read(b.LOG)), 1)
    def test_halt_refuses_before_logging_or_trading(self):
        b.HALT.write_text("drawdown")
        with self.assertRaisesRegex(ValueError, "halted"): b.alpha_trade("ETH_USDT", "long", 2.0, 4.0, "x")
        self.assertEqual((self.made, self.opened), ([], []))
    def test_daily_loss_halt_refuses(self):
        b.LOG.write_text(json.dumps({"coin": "A", "opened": NOW, "closed": NOW, "pnl_usd": -50.0}) + "\n")
        with self.assertRaisesRegex(ValueError, "daily loss"): b.alpha_trade("ETH_USDT", "long", 2.0, 4.0, "x")
        self.assertEqual(self.opened, [])
    def test_already_holding_refused(self):
        b.alpha_trade("ETH_USDT", "long", 2.0, 4.0, "x")
        with self.assertRaisesRegex(ValueError, "already holding"): b.alpha_trade("ETH_USDT", "long", 2.0, 4.0, "again")
        self.assertEqual(len(self.opened), 1)
    def test_flat_is_not_a_trade(self):
        with self.assertRaises(ValueError): b.alpha_trade("ETH_USDT", "flat", 2.0, 4.0, "x")
    def test_failed_order_keeps_the_call_but_not_a_trade(self):
        def boom(*a, **k): raise SystemExit("max_open 3 reached")
        b.T.open_trade = boom
        with self.assertRaisesRegex(ValueError, "trade not opened"): b.alpha_trade("ETH_USDT", "long", 2.0, 4.0, "x")
        self.assertEqual((len(self.made), b.read(b.LOG)), (1, []))
    def test_close_rejects_bots_own_trades(self):
        b.LOG.write_text(json.dumps({"coin": "SOL_USDT", "setup": "setup_trend", "opened": NOW, "horizon_h": 24}) + "\n")
        with self.assertRaisesRegex(ValueError, "no open Alpha trade"): b.alpha_close("SOL_USDT")

if __name__ == "__main__": unittest.main()


class EquityFileOnlyOnNewPeak(unittest.TestCase):
    def test_reads_do_not_rewrite_the_file(self):
        import tempfile, pathlib
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "equity.json"; f.write_text(json.dumps({"peak": 1000.0, "equity": 1000.0, "ts": 1}))
            with mock.patch.object(b, "EQUITY", f), mock.patch.object(b.T, "api", return_value={"total": "990"}):
                self.assertEqual(b.equity_now(), (990.0, 1000.0))
                self.assertEqual(json.loads(f.read_text())["ts"], 1)            # unchanged: below peak
            with mock.patch.object(b, "EQUITY", f), mock.patch.object(b.T, "api", return_value={"total": "1010"}):
                self.assertEqual(b.equity_now(), (1010.0, 1010.0))
                self.assertEqual(json.loads(f.read_text())["peak"], 1010.0)     # new peak: saved

    def test_first_run_creates_the_file(self):
        import tempfile, pathlib
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "equity.json"
            with mock.patch.object(b, "EQUITY", f), mock.patch.object(b.T, "api", return_value={"total": "500"}):
                b.equity_now()
            self.assertEqual(json.loads(f.read_text())["peak"], 500.0)

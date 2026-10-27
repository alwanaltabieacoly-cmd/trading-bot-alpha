import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "research"))
import gate_config as c

def cfg(**kw):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "g.json"; p.write_text(json.dumps(kw)); return c.load(p)

class GateConfig(unittest.TestCase):
    def test_missing_file_gives_defaults(self): self.assertEqual(c.load(Path("nope.json")), c.DEFAULTS)
    def test_override_one_value(self): self.assertEqual(cfg(max_open=2)["max_open"], 2)
    def test_repo_file_equals_defaults(self): self.assertEqual(c.load(), c.DEFAULTS)
    def test_risk_over_range_stops(self):
        with self.assertRaises(SystemExit): cfg(explore_risk_pct=5)
    def test_text_value_stops(self):
        with self.assertRaises(SystemExit): cfg(max_open="3")
    def test_unknown_key_stops(self):
        with self.assertRaises(SystemExit): cfg(risk=1)
    def test_explore_above_full_risk_stops(self):
        with self.assertRaises(SystemExit): cfg(explore_risk_pct=0.5, risk_pct=0.3)
    def test_cannot_loosen_any_limit_past_the_approved_edge(self):
        for k, v in (("explore_risk_pct", 0.26), ("risk_pct", 1.01), ("daily_loss_pct", 1.5), ("drawdown_pct", 5.5), ("max_open", 4), ("max_leverage", 4),
                     ("max_notional_x_equity", 3.5), ("alpha_max_trades_per_day", 3), ("explore_days", 9), ("proven_days", 29)):
            with self.subTest(k), self.assertRaises(SystemExit): cfg(**{k: v})
    def test_can_tighten(self): self.assertEqual(cfg(explore_risk_pct=0.1, daily_loss_pct=0.5, drawdown_pct=3, max_open=1)["max_open"], 1)
    def test_fractions_in_whole_number_fields_stop(self):
        for k in ("max_open", "max_leverage"):
            with self.subTest(k), self.assertRaises(SystemExit): cfg(**{k: 2.5})
    def test_bad_files_fall_back_to_defaults_not_a_crash(self):
        with tempfile.TemporaryDirectory() as d:
            for text in ("{not json", "[]", "null", '{"max_open": 99}'):
                p = Path(d) / "g.json"; p.write_text(text); self.assertEqual(c.safe_load(p), c.DEFAULTS, text)
    def test_explore_days_not_below_proven_stops(self):
        with self.assertRaises(SystemExit): cfg(explore_days=30, proven_days=30)

if __name__ == "__main__": unittest.main()

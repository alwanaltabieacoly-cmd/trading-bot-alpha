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
    def test_explore_days_not_below_proven_stops(self):
        with self.assertRaises(SystemExit): cfg(explore_days=30, proven_days=30)

if __name__ == "__main__": unittest.main()

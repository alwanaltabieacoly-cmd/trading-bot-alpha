import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "research"))
import gate_trader as t

SPEC = {"quanto_multiplier": "0.0001", "order_price_round": "0.1", "order_size_min": 1}

class Plan(unittest.TestCase):
    def test_long_stop_below_target_above(self):
        p = t.plan("BTC_USDT", "long", 80000, 1.0, 2.0, 1000, SPEC)
        self.assertLess(p["stop"], 80000); self.assertGreater(p["target"], 80000); self.assertGreater(p["size"], 0)
    def test_short_stop_above_target_below(self):
        p = t.plan("BTC_USDT", "short", 80000, 1.0, 2.0, 1000, SPEC)
        self.assertGreater(p["stop"], 80000); self.assertLess(p["target"], 80000); self.assertLess(p["size"], 0)
    def test_risk_never_exceeds_limit(self):
        p = t.plan("BTC_USDT", "long", 80000, 1.0, 2.0, 1000, SPEC)
        self.assertLessEqual(p["risk_usd"], 10.0)
    def test_notional_capped(self):
        p = t.plan("BTC_USDT", "long", 80000, 0.1, 2.0, 1000, SPEC)  # tiny stop would allow huge size
        self.assertLessEqual(p["notional"], 3000.0)
    def test_stop_is_mandatory(self):
        for bad in (0, -1, 11):
            with self.assertRaises(ValueError): t.plan("BTC_USDT", "long", 80000, bad, 2.0, 1000, SPEC)
    def test_too_small_account_refused(self):
        with self.assertRaises(ValueError): t.plan("BTC_USDT", "long", 80000, 1.0, 2.0, 5, SPEC)

class Trigger(unittest.TestCase):
    def rule(self, side, kind): return t.trigger_body("BTC_USDT", side, 1, kind)["trigger"]["rule"]
    def test_rules(self):
        self.assertEqual(self.rule("long", "stop"), 2)    # price <= trigger
        self.assertEqual(self.rule("long", "target"), 1)  # price >= trigger
        self.assertEqual(self.rule("short", "stop"), 1)
        self.assertEqual(self.rule("short", "target"), 2)
    def test_closes_whole_position_reduce_only(self):
        b = t.trigger_body("BTC_USDT", "long", 79000, "stop")
        self.assertEqual(b["order_type"], "close-long-position"); self.assertTrue(b["initial"]["reduce_only"]); self.assertEqual(b["initial"]["size"], 0)
        self.assertEqual(t.trigger_body("BTC_USDT", "short", 1, "stop")["order_type"], "close-short-position")

class Safety(unittest.TestCase):
    def test_testnet_only(self): self.assertEqual(t.ENV, "testnet")

if __name__ == "__main__": unittest.main()

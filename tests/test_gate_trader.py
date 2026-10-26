import sys, unittest
from decimal import Decimal
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

class Rounding(unittest.TestCase):
    def test_no_float_noise(self):   # the bug that made Gate reject BTC stops: 793649 * 0.1 = 79364.90000000001
        self.assertEqual(t.fmt(t.round_to(79364.9000000001, 0.1)), "79364.9")
    def test_many_prices_are_clean(self):
        for step in (0.1, 0.01, 0.001, 0.00001, 0.5, 1):
            for i in range(1, 3000, 7):
                px = t.round_to(i * 1.0371 * step * 13.7, step); s = t.fmt(px)
                self.assertLessEqual(-Decimal(s).as_tuple().exponent if "." in s else 0, -Decimal(repr(step)).as_tuple().exponent, (step, px, s))
    def test_small_prices_not_scientific(self): self.assertEqual(t.fmt(4.2e-06), "0.0000042")
    def test_snaps_to_step(self): self.assertEqual(t.fmt(t.round_to(1.2913, 0.0001)), "1.2913")

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

class EmptyBook(unittest.TestCase):
    """PEPE_USDT on the testnet had 0 asks: Gate answered CONTRACT_NO_COUNTER. Refuse before any order is sent."""
    def run_open(self, side, book):
        calls = []
        def fake(method, path, query="", body=None):
            calls.append((method, path))
            if path == "/futures/usdt/accounts": return {"total": "1000"}
            if path == "/futures/usdt/positions": return []
            if path == "/futures/usdt/order_book": return book
            raise AssertionError(f"unexpected {method} {path}")
        old, t.api = t.api, fake
        try: t.open_trade("PEPE_USDT", side, 5.0, 10.0)
        finally: t.api = old
        return calls
    def test_long_refused_without_asks(self):
        with self.assertRaisesRegex(SystemExit, "no asks"): self.run_open("long", {"asks": [], "bids": [{"p": "1", "s": 1}]})
    def test_short_refused_without_bids(self):
        with self.assertRaisesRegex(SystemExit, "no bids"): self.run_open("short", {"asks": [{"p": "1", "s": 1}], "bids": []})

if __name__ == "__main__": unittest.main()

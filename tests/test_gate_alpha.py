import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "research"))
import gate_alpha as G, gate_judge as J

NOW = 1793048400 + 3000   # a Monday-ish instant; only the arithmetic matters
LIQ = {"BTC_USDT", "ETH_USDT"}

class MakeCall(unittest.TestCase):
    def setUp(self): self.p = Path(tempfile.mkdtemp()) / "alpha_calls.jsonl"
    def call(self, **kw):
        a = dict(coin="BTC_USDT", call="long", stop_pct=1.5, target_pct=3.0, why="sweep of the low then reclaim", path=self.p, now=NOW, mark=80000.0, liquid=LIQ); a.update(kw)
        return G.make_call(**a)
    def test_entry_is_the_mark_price_given_by_gate_not_the_caller(self):
        r = self.call(); self.assertEqual(r["entry"], 80000.0); self.assertEqual(r["ts"], NOW)
    def test_day_key_matches_rules_analyst_day(self):   # the analyst uses the open time of the last CLOSED daily bar
        self.assertEqual(self.call()["day"], NOW // 86400 * 86400 - 86400)
    def test_one_call_per_coin_per_day_and_append_only(self):
        self.call()
        with self.assertRaises(ValueError): self.call(call="short")
        self.assertEqual(len(self.p.read_text().splitlines()), 1)
    def test_other_coin_same_day_ok(self): self.call(); self.call(coin="ETH_USDT"); self.assertEqual(len(self.p.read_text().splitlines()), 2)
    def test_next_day_ok(self): self.call(); self.call(now=NOW + 86400)
    def test_stop_is_mandatory(self):
        for bad in (0, -1, 10.5):
            with self.assertRaises(ValueError): self.call(stop_pct=bad)
    def test_reason_is_mandatory(self):
        for bad in ("", "   "):
            with self.assertRaises(ValueError): self.call(why=bad)
    def test_illiquid_or_unknown_coin_refused(self):
        with self.assertRaises(ValueError): self.call(coin="DOGE_USDT")
    def test_unknown_tag_refused(self):
        with self.assertRaises(ValueError): self.call(tags=["vibes"])
    def test_flat_is_recorded_but_needs_no_stop(self):
        r = self.call(call="flat", stop_pct=0, target_pct=0); self.assertEqual(r["call"], "flat")
    def test_alpha_tag_is_always_present(self): self.assertEqual(self.call(tags=["news"])["tags"], ["alpha", "news"])

class Window(unittest.TestCase):
    def test_starts_at_the_first_full_hour_after_the_call(self):
        ks, ready = J.window(3600 * 100 + 3000, 24)   # called at 100:50
        self.assertEqual(ks[0], 3600 * 101); self.assertEqual(len(ks), 24); self.assertEqual(ready, 3600 * 125)
    def test_call_exactly_on_the_hour_uses_that_hour(self):
        self.assertEqual(J.window(3600 * 100, 24)[0][0], 3600 * 100)
    def test_late_and_early_callers_get_the_same_number_of_bars(self):
        self.assertEqual(len(J.window(3600 * 100 + 60, 24)[0]), len(J.window(3600 * 100 + 3500, 24)[0]))
    def test_pre_call_prices_are_never_in_the_window(self):
        for off in (1, 600, 3599): self.assertGreater(J.window(3600 * 100 + off, 24)[0][0], 3600 * 100 + off - 1)

class Versus(unittest.TestCase):
    def row(self, coin, day, net, call="long"): return {"coin": coin, "day": day, "net": net, "base": 0.0, "call": call}
    def test_same_day_calls_count_as_one_day(self):
        v = J.versus([self.row("A", 1, 1), self.row("B", 1, 1), self.row("C", 1, 1)], [])
        self.assertEqual((v["rules"]["calls"], v["rules"]["days"]), (3, 1))
    def test_overlap_and_exclusive_calls(self):
        v = J.versus([self.row("A", 1, 1), self.row("B", 1, 2)], [self.row("A", 1, -1, "short"), self.row("C", 1, 5)])
        self.assertEqual((v["both"]["n"], v["both"]["same_direction"]), (1, 0)); self.assertEqual((v["rules_only"]["n"], v["alpha_only"]["n"]), (1, 1))
        self.assertAlmostEqual(v["alpha_only"]["mean"], 5)
    def test_empty_sides_do_not_crash(self): self.assertIn("too early", "\n".join(J.versus_lines([], [])))
    def test_no_winner_before_30_days(self):
        rows = [self.row("A", d, 1) for d in range(29)]; self.assertIn("too early", J.versus_lines(rows, rows)[-1])

if __name__ == "__main__": unittest.main()

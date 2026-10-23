import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents import critic_agent, decision_agent  # noqa: E402


def _market(timeframes, pair="EURUSD"):
    return {"pairs": {pair: {"timeframes": timeframes}}}


class CriticMultiAssetTest(unittest.TestCase):
    def test_daily_only_bull_is_allowed(self):
        # Equities/FX only have 1d data: must not be vetoed for missing 1h/4h.
        market = _market({"1d": {"available": True, "regime": "bull"}})
        entry = critic_agent.analyze(None, market, {"EURUSD": {"action": "allow"}})
        self.assertEqual(entry["recommendation"], "allow", entry["blockers"])
        self.assertEqual(entry["pair_recommendations"]["EURUSD"], "allow")

    def test_bear_on_any_available_timeframe_blocks(self):
        market = _market({
            "4h": {"available": True, "regime": "bear"},
            "1d": {"available": True, "regime": "bull"},
        })
        entry = critic_agent.analyze(None, market, {"EURUSD": {"action": "allow"}})
        self.assertEqual(entry["recommendation"], "block")
        self.assertTrue(any("bear regime" in b for b in entry["blockers"]))

    def test_no_regime_data_fails_closed(self):
        market = _market({"1d": {"available": False}, "4h": {"available": False}})
        entry = critic_agent.analyze(None, market, {"EURUSD": {"action": "allow"}})
        self.assertEqual(entry["recommendation"], "block")
        self.assertTrue(any("no regime data" in b for b in entry["blockers"]))

    def test_block_requests_are_not_vetoed_again(self):
        market = _market({"1d": {"available": True, "regime": "range"}})
        entry = critic_agent.analyze(None, market, {"EURUSD": {"action": "block"}})
        self.assertEqual(entry["recommendation"], "allow")
        self.assertEqual(entry["pair_recommendations"]["EURUSD"], "block")


class FallbackMultiAssetTest(unittest.TestCase):
    def test_daily_bull_allows(self):
        market = _market({"1d": {"available": True, "regime": "bull"}})
        result = decision_agent._fallback(["EURUSD"], 0.5, market)
        self.assertEqual(result["EURUSD"]["action"], "allow")
        self.assertIn("1d", result["EURUSD"]["rationale"])

    def test_4h_preferred_when_available(self):
        market = _market({
            "4h": {"available": True, "regime": "bull"},
            "1d": {"available": True, "regime": "range"},
        }, pair="BTC/USDT")
        result = decision_agent._fallback(["BTC/USDT"], 0.5, market)
        self.assertEqual(result["BTC/USDT"]["action"], "allow")
        self.assertIn("4h", result["BTC/USDT"]["rationale"])

    def test_missing_data_blocks(self):
        market = _market({"1d": {"available": False}})
        result = decision_agent._fallback(["EURUSD"], 0.5, market)
        self.assertEqual(result["EURUSD"]["action"], "block")
        self.assertIn("no", result["EURUSD"]["rationale"])


if __name__ == "__main__":
    sys.exit(unittest.main())

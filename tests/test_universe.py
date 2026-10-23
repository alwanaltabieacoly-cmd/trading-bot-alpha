import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from agents import universe  # noqa: E402
import scan_shortlist  # noqa: E402


def _frame(n=80):
    dates = pd.date_range("2024-01-01", periods=n, freq="D", tz="UTC")
    close = pd.Series(np.linspace(100.0, 130.0, n))
    return pd.DataFrame({
        "date": dates,
        "open": close,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": 1000.0,
    })


class UniverseClassifyTest(unittest.TestCase):
    def test_crypto_forms(self):
        for symbol in ("BTC", "BTC/USDT", "btc-usd", "BTCUSDT"):
            self.assertEqual(universe.classify(symbol), "crypto", symbol)

    def test_equity_and_forex(self):
        self.assertEqual(universe.classify("AAPL"), "equity")
        self.assertEqual(universe.classify("NVDA"), "equity")
        self.assertEqual(universe.classify("EURUSD"), "forex")
        self.assertEqual(universe.classify("EURUSD=X"), "forex")
        self.assertEqual(universe.classify("XAUUSD"), "forex")

    def test_unknown_is_none(self):
        self.assertIsNone(universe.classify("NOT_A_THING"))

    def test_forex_ticker_fallbacks(self):
        self.assertEqual(universe._yahoo_tickers("XAUUSD"), ("XAUUSD=X", "GC=F"))
        self.assertEqual(universe._yahoo_tickers("XAGUSD"), ("XAGUSD=X", "SI=F"))
        self.assertEqual(universe._yahoo_tickers("EURUSD"), ("EURUSD=X",))
        self.assertEqual(universe._yahoo_tickers("AAPL"), ("AAPL",))

    def test_display_and_decision_symbols(self):
        self.assertEqual(universe.display_symbol("BTC/USDT"), "BTC/USD")
        self.assertEqual(universe.decision_symbol("BTC"), "BTC/USDT")
        self.assertEqual(universe.display_symbol("AAPL"), "AAPL")
        self.assertEqual(universe.decision_symbol("EURUSD=X"), "EURUSD")

    def test_cache_dirs_split_by_class(self):
        self.assertIn("scan", universe.cache_path("BTC", "4h").as_posix())
        self.assertIn("universe", universe.cache_path("AAPL", "1d").as_posix())
        self.assertIn("universe", universe.cache_path("EURUSD", "1d").as_posix())

    def test_watchlists(self):
        self.assertIn("BTC", universe.watchlist("crypto"))
        self.assertIn("NVDA", universe.watchlist("equity"))
        self.assertIn("USDJPY", universe.watchlist("forex"))
        self.assertEqual(len(universe.watchlist("equity", 3)), 3)

    def test_default_timeframes(self):
        self.assertEqual(universe.DEFAULT_TF["crypto"], "4h")
        self.assertEqual(universe.DEFAULT_TF["equity"], "1d")
        self.assertEqual(universe.DEFAULT_TF["forex"], "1d")


class UniverseScoreTest(unittest.TestCase):
    def test_score_equity_from_cache(self):
        with mock.patch.object(universe, "load", return_value=_frame()):
            record, reason = universe.score("AAPL")
        self.assertIsNone(reason)
        self.assertEqual(record["asset_class"], "equity")
        self.assertEqual(record["tf"], "1d")
        self.assertEqual(record["pair"], "AAPL")
        self.assertIn("profit_score", record)

    def test_score_missing_cache_reports_reason(self):
        with mock.patch.object(universe, "load", return_value=None):
            record, reason = universe.score("EURUSD")
        self.assertIsNone(record)
        self.assertIn("no cached", reason)

    def test_unknown_symbol_skipped(self):
        record, reason = universe.score("WAT")
        self.assertIsNone(record)
        self.assertIn("unknown asset class", reason)

    def test_refresh_reports_unknown_symbol(self):
        status = universe.refresh(["WAT"])
        self.assertFalse(status["WAT"]["ok"])

    def test_snapshot_has_all_classes(self):
        snap = universe.snapshot()
        self.assertEqual(set(snap["classes"]), {"crypto", "equity", "forex"})


class ShortlistTest(unittest.TestCase):
    ROWS = [
        {"pair": "BCH/USD", "asset_class": "crypto", "profit_score": 1.7, "momentum": 1, "micro_score": 1},
        {"pair": "DOGE/USD", "asset_class": "crypto", "profit_score": 0.5, "momentum": 1, "micro_score": 1},
        {"pair": "ADA/USD", "asset_class": "crypto", "profit_score": 0.2, "momentum": 1, "micro_score": 1},
        {"pair": "BTC/USD", "asset_class": "crypto", "profit_score": -0.3, "momentum": 1, "micro_score": 1},
        {"pair": "NVDA", "asset_class": "equity", "profit_score": 0.9, "momentum": 1, "micro_score": 1},
        {"pair": "AAPL", "asset_class": "equity", "profit_score": 0.4, "momentum": 1, "micro_score": 1},
        {"pair": "MSFT", "asset_class": "equity", "profit_score": 0.1, "momentum": 1, "micro_score": 1},
        {"pair": "EURUSD", "asset_class": "forex", "profit_score": 0.6, "momentum": 1, "micro_score": 1},
    ]

    def test_quota_and_positive_only(self):
        picks = scan_shortlist.select(self.ROWS, quota={"crypto": 2, "equity": 1, "forex": 1})
        symbols = {p["decision_symbol"] for p in picks}
        self.assertEqual(symbols, {"BCH/USDT", "DOGE/USDT", "NVDA", "EURUSD"})
        self.assertNotIn("BTC/USDT", symbols)  # negative score excluded

    def test_rows_without_asset_class_default_to_crypto(self):
        rows = [{"pair": "ETH/USD", "profit_score": 0.8}]
        picks = scan_shortlist.select(rows, quota={"crypto": 1, "equity": 0, "forex": 0})
        self.assertEqual(picks[0]["decision_symbol"], "ETH/USDT")

    def test_empty_when_nothing_positive(self):
        picks = scan_shortlist.select(
            [{"pair": "BTC/USD", "asset_class": "crypto", "profit_score": -1.0}])
        self.assertEqual(picks, [])


class ScannerClassDispatchTest(unittest.TestCase):
    def test_equity_class_uses_universe(self):
        import asset_scanner

        rec = {"pair": "AAPL", "asset_class": "equity", "profit_score": 0.5}
        with mock.patch.object(asset_scanner.universe, "watchlist", return_value=["AAPL"]), \
                mock.patch.object(asset_scanner.universe, "score", return_value=(rec, None)):
            results = asset_scanner.run(asset_class="equity", as_json=True)
        self.assertEqual(results[0]["asset_class"], "equity")

    def test_all_classes_merge_and_sort(self):
        import asset_scanner

        def fake_score(symbol, fetch_missing=False):
            score = 0.9 if symbol == "AAPL" else 0.2
            return {"pair": symbol, "asset_class": universe.classify(symbol) or "crypto",
                    "profit_score": score}, None

        with mock.patch.object(asset_scanner.universe, "watchlist",
                               side_effect=lambda cls, limit=None: ["AAPL"] if cls == "equity" else ["EURUSD"]), \
                mock.patch.object(asset_scanner.universe, "score", side_effect=fake_score), \
                mock.patch.object(asset_scanner, "_watchlist", return_value=[]):
            results = asset_scanner.run(asset_class="all", as_json=True)
        self.assertEqual([r["pair"] for r in results], ["AAPL", "EURUSD"])


if __name__ == "__main__":
    sys.exit(unittest.main())

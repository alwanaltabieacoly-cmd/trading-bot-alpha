import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import asset_scanner

RECORD = {
    "pair": "BTC/USD", "tf": "4h", "close": 81000.0, "momentum": 0.1,
    "micro_score": 0.2, "vol_regime": 0.0, "volume_spike": 0.0,
    "candle_position": 0.0, "n_bars": 100, "profit_score": 0.9,
}


class TestScannerJsonPurity(unittest.TestCase):
    """asset_scan.json is committed and parsed by summary_scan.py, so stdout
    must be pure JSON in --json mode and every skip must be explained."""

    def _run(self, watchlist, score):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(asset_scanner, "_watchlist", return_value=watchlist), \
                mock.patch.object(asset_scanner, "_score_pair", side_effect=score):
            with redirect_stdout(out), redirect_stderr(err):
                results = asset_scanner.run(as_json=True)
        return results, out.getvalue(), err.getvalue()

    def test_json_mode_stdout_is_pure_json(self):
        results, out, err = self._run(["BTC"], lambda base, tf="4h", fetch_missing=False: (RECORD, None))
        self.assertEqual(len(results), 1)
        self.assertEqual(json.loads(out), [RECORD])
        self.assertIn("scanned 1/1", err)

    def test_skips_are_reported_not_silent(self):
        results, out, err = self._run(
            ["ADA"], lambda base, tf="4h", fetch_missing=False: (None, "no cached 4h candles"))
        self.assertEqual(results, [])
        self.assertEqual(json.loads(out), [])
        self.assertIn("skip ADA/USD", err)
        self.assertIn("no cached 4h candles", err)

    def test_one_bad_pair_does_not_kill_the_scan(self):
        def boom(base, tf="4h", fetch_missing=False):
            raise RuntimeError("kaboom")

        results, out, err = self._run(["ADA"], boom)
        self.assertEqual(results, [])
        self.assertEqual(json.loads(out), [])
        self.assertIn("kaboom", err)

    def test_log_goes_to_stderr_in_json_mode(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            asset_scanner._log("hello", as_json=True)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("hello", err.getvalue())

    def test_results_ranked_by_profit_score(self):
        low = dict(RECORD, pair="ETH/USD", profit_score=-1.0)
        high = dict(RECORD, profit_score=2.0)
        results, _out, _err = self._run(
            ["ETH", "BTC"],
            lambda base, tf="4h", fetch_missing=False: (low if base == "ETH" else high, None),
        )
        self.assertEqual([r["profit_score"] for r in results], [2.0, -1.0])


class TestScannerUniverse(unittest.TestCase):
    def test_cached_bases_only_lists_existing_parquet(self):
        bases = asset_scanner._cached_bases("4h")
        self.assertIsInstance(bases, list)
        # Whatever the cache holds, everything listed must have a parquet file.
        import os
        for base in bases:
            self.assertTrue(os.path.exists(os.path.join(asset_scanner.config.DATA_DIR, f"{base}_4h.parquet")))

    def test_pairs_argument_normalises_symbols(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(asset_scanner, "_score_pair",
                               side_effect=lambda base, tf="4h", fetch_missing=False: (None, "x")):
            with redirect_stdout(out), redirect_stderr(err):
                asset_scanner.run(pairs=["btc/usd", "ETH-USD"], as_json=True)
        self.assertIn("skip BTC/USD", err.getvalue())
        self.assertIn("skip ETH/USD", err.getvalue())


if __name__ == "__main__":
    sys.exit(unittest.main())

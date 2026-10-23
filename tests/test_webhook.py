"""Integration tests for the money path: the TradingView webhook.

This is the only code that can execute a trade. It had no CI coverage before,
so the tests here are the permanent guard against a silent bad fill:
  - bad secret rejected
  - evidence gate blocks by default
  - deliberation block / zero size blocks
  - explicit qty honoured, stake fallback works
  - sell/close are risk exits and never gated
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

import webhook_server  # noqa: E402

SECRET = "test-secret"


def _gate_allow(action="allow", size=0.5):
    return {
        "allowed": True,
        "reasons": [],
        "evidence": {
            "decision_pair": {"action": action, "size": size, "confidence": 0.7, "rationale": "test"},
            "scan": {"pair": "BTC/USD", "profit_score": 1.0},
        },
    }


def _gate_block(reason="no fresh evidence"):
    return {"allowed": False, "reasons": [reason], "evidence": {}}


class WebhookMoneyPathTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.state = self.dir / "state.json"
        self.log = self.dir / "trades.jsonl"
        self.state.write_text(json.dumps({"cash": 1000.0, "positions": {}, "equity": 1000.0, "trades": []}))
        self.patches = [
            mock.patch.object(webhook_server, "WEBHOOK_SECRET", SECRET),
            mock.patch.object(webhook_server, "PAPER_STATE_PATH", self.state),
            mock.patch.object(webhook_server, "LOG_PATH", self.log),
            mock.patch.object(webhook_server, "_time_gate", return_value=(True, "ok")),
        ]
        for p in self.patches:
            p.start()
        self.client = TestClient(webhook_server.app)

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def _post(self, payload, secret=SECRET):
        return self.client.post("/webhook/tv", json=payload, headers={"x-tv-secret": secret})

    def _buy(self, **overrides):
        payload = {"symbol": "BTC", "action": "buy", "price": 50000.0, "secret": SECRET}
        payload.update(overrides)
        return self._post(payload)

    # --- security ---------------------------------------------------------
    def test_bad_secret_is_rejected(self):
        self.assertEqual(self._post({"symbol": "BTC", "action": "buy", "price": 1.0}, secret="wrong").status_code, 401)

    # --- gate is default-deny --------------------------------------------
    def test_gate_block_prevents_execution(self):
        with mock.patch.object(webhook_server.evidence_gate, "check_entry", return_value=_gate_block()):
            body = self._buy().json()
        self.assertFalse(body["executed"])
        self.assertIn("evidence gate", body["reason"])

    def test_deliberation_block_prevents_execution(self):
        with mock.patch.object(webhook_server.evidence_gate, "check_entry", return_value=_gate_allow(action="block", size=0.0)):
            body = self._buy().json()
        self.assertFalse(body["executed"])
        self.assertIn("deliberation blocked", body["reason"])

    def test_zero_size_prevents_execution(self):
        with mock.patch.object(webhook_server.evidence_gate, "check_entry", return_value=_gate_allow(action="allow", size=0.0)):
            body = self._buy().json()
        self.assertFalse(body["executed"])
        self.assertIn("size=0", body["reason"])

    # --- allowed path -----------------------------------------------------
    def test_allowed_buy_with_explicit_qty_executes(self):
        with mock.patch.object(webhook_server.evidence_gate, "check_entry", return_value=_gate_allow()):
            body = self._buy(qty=0.25).json()
        self.assertTrue(body["executed"], body)
        rows = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(rows[-1]["qty"], 0.25)
        state = json.loads(self.state.read_text())
        self.assertAlmostEqual(state["positions"]["BTC"]["qty"], 0.25)

    def test_allowed_buy_without_qty_uses_stake(self):
        with mock.patch.object(webhook_server.evidence_gate, "check_entry", return_value=_gate_allow()):
            body = self._buy().json()
        self.assertTrue(body["executed"], body)
        state = json.loads(self.state.read_text())
        # default stake = 10% of cash / price
        self.assertAlmostEqual(state["positions"]["BTC"]["qty"], (1000.0 * 0.10) / 50000.0, places=9)

    # --- routing ----------------------------------------------------------
    def test_equity_scalp_blocked_without_alpha_evidence(self):
        with mock.patch.object(webhook_server.evidence_gate, "check_vibe",
                               return_value={"allowed": False, "reasons": ["no alpha evidence"], "evidence": {}}):
            body = self._post({"symbol": "AAPL", "action": "buy", "price": 200.0,
                               "strategy": "scalp", "secret": SECRET}).json()
        self.assertFalse(body["executed"])
        self.assertIn("evidence gate", body["reason"])

    def test_equity_scalp_blocked_for_unknown_strategy(self):
        with mock.patch.object(webhook_server.evidence_gate, "check_vibe",
                               return_value={"allowed": True, "reasons": [], "evidence": {"vibe": {"best_alpha": "x"}}}):
            body = self._post({"symbol": "AAPL", "action": "buy", "price": 200.0,
                               "strategy": "mystery", "secret": SECRET}).json()
        self.assertFalse(body["executed"])
        self.assertIn("unknown scalp strategy", body["reason"])

    # --- exits are never gated -------------------------------------------
    def test_sell_without_position_is_noop(self):
        body = self._post({"symbol": "BTC", "action": "sell", "price": 50000.0, "secret": SECRET}).json()
        self.assertFalse(body["executed"])
        self.assertIn("no position", body["reason"])

    def test_close_position_executes_without_gate(self):
        self.state.write_text(json.dumps({
            "cash": 0.0, "positions": {"BTC": {"qty": 1.0, "avg": 40000.0}},
            "equity": 40000.0, "trades": [],
        }))
        with mock.patch.object(webhook_server.evidence_gate, "check_entry",
                               side_effect=AssertionError("gate must not run on exits")):
            body = self._post({"symbol": "BTC", "action": "close", "price": 50000.0, "secret": SECRET}).json()
        self.assertTrue(body["executed"], body)
        state = json.loads(self.state.read_text())
        self.assertEqual(state["positions"]["BTC"]["qty"], 0.0)


if __name__ == "__main__":
    sys.exit(unittest.main())

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import daily_brief  # noqa: E402

PAYLOAD = {
    "date": "2026-10-23",
    "generated_at": "2026-10-23T21:15:00+00:00",
    "decision": {"path": "reports/decisions/2026-10-23_1700.json",
                 "generated_at": "2026-10-23T17:50:00+00:00", "pairs": ["USDJPY", "AAPL"]},
    "gate": {
        "USDJPY": {"entry": True, "evidence_ok": True, "reasons": [], "scan_score": 2.25,
                   "action": "allow", "size": 0.25},
        "AAPL": {"entry": False, "evidence_ok": False,
                 "reasons": ["asset scan ranks AAPL at -0.5 (<0)"],
                 "scan_score": -0.5, "action": "allow", "size": 0.2},
    },
    "scan": [
        {"pair": "USDJPY", "asset_class": "forex", "profit_score": 2.25, "momentum": 0.3, "micro_score": 0.1},
        {"pair": "AAPL", "asset_class": "equity", "profit_score": 1.79, "momentum": 0.2, "micro_score": 0.0},
    ],
    "shortlist": ["USDJPY", "AAPL"],
    "vibe": {"zoo": "academic", "universe": "sp500", "period": "2024-2025", "age_hours": 1.0,
             "top": [{"alpha": "academic_carhart_mom", "ir": 0.12, "ic_mean": 0.028, "ic_count": 249}]},
    "learning": {"n": 32, "accuracy": 0.562,
                 "lessons": ["SOL/USDT accuracy 38% over 8 labels - exclude"]},
}


class DailyBriefTest(unittest.TestCase):
    def test_markdown_has_all_sections(self):
        md = daily_brief.build_markdown(PAYLOAD)
        for needle in ("# Trading brief", "## Gate verdicts", "## Scan leaders",
                       "## Deliberation shortlist", "## Alpha evidence", "## Learning", "## How to act"):
            self.assertIn(needle, md)
        self.assertIn("USDJPY", md)
        self.assertIn("ALLOW", md)
        self.assertIn("BLOCK", md)
        self.assertIn("academic_carhart_mom", md)
        self.assertIn("SOL/USDT accuracy", md)

    def test_evidence_ok_but_deliberation_blocked_is_not_an_entry(self):
        payload = dict(PAYLOAD)
        payload["gate"] = {"ETH/USDT": {"entry": False, "evidence_ok": True,
                                        "reasons": ["deliberation block (analyst=block)"],
                                        "scan_score": -0.2, "action": "block", "size": 0.0}}
        md = daily_brief.build_markdown(payload)
        self.assertIn("| ETH/USDT | BLOCK | ok | block |", md)
        self.assertIn("deliberation block", md)

    def test_empty_payload_fails_closed_language(self):
        md = daily_brief.build_markdown({"date": "2026-10-23", "decision": None, "gate": {},
                                         "scan": [], "shortlist": [], "vibe": None, "learning": None})
        self.assertIn("fail closed", md)
        self.assertIn("No scan artifact", md)
        self.assertIn("No learning digest", md)

    def test_collect_never_raises_on_missing_artifacts(self):
        payload = daily_brief.collect()
        self.assertIn("date", payload)
        self.assertIsInstance(payload.get("gate"), dict)


if __name__ == "__main__":
    sys.exit(unittest.main())

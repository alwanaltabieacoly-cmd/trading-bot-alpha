import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import system_check  # noqa: E402

NOW = datetime(2026, 10, 23, 21, 0, tzinfo=timezone.utc)


class SystemCheckTest(unittest.TestCase):
    def setUp(self):
        system_check.STATE = {"PASS": 0, "WARN": 0, "FAIL": 0}
        system_check.RESULTS = []
        self.tmp = Path(tempfile.mkdtemp())

    def _write(self, rel, payload, age_hours=1.0):
        path = self.tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = payload if isinstance(payload, str) else json.dumps(payload)
        path.write_text(text, encoding="utf-8")
        stamp = (NOW - timedelta(hours=age_hours)).timestamp()
        import os
        os.utime(path, (stamp, stamp))
        return path

    def test_fresh_artifact_passes(self):
        self._write("research/reports/asset_scan.json", [{"pair": "BTC/USD"}])
        with mock.patch.object(system_check, "ROOT", self.tmp):
            system_check._check_artifact("scan", "research/reports/asset_scan.json", list, 26.0, now=NOW)
        self.assertEqual(system_check.RESULTS[0]["status"], "PASS")

    def test_stale_artifact_fails(self):
        self._write("research/reports/asset_scan.json", [{"pair": "BTC/USD"}], age_hours=40)
        with mock.patch.object(system_check, "ROOT", self.tmp):
            system_check._check_artifact("scan", "research/reports/asset_scan.json", list, 26.0, now=NOW)
        self.assertEqual(system_check.RESULTS[0]["status"], "FAIL")
        self.assertIn("stale", system_check.RESULTS[0]["detail"])

    def test_empty_list_fails(self):
        self._write("research/reports/asset_scan.json", [])
        with mock.patch.object(system_check, "ROOT", self.tmp):
            system_check._check_artifact("scan", "research/reports/asset_scan.json", list, 26.0, now=NOW)
        self.assertEqual(system_check.RESULTS[0]["status"], "FAIL")
        self.assertIn("empty", system_check.RESULTS[0]["detail"])

    def test_unparseable_json_fails(self):
        self._write("research/reports/asset_scan.json", "{not json")
        with mock.patch.object(system_check, "ROOT", self.tmp):
            system_check._check_artifact("scan", "research/reports/asset_scan.json", list, 26.0, now=NOW)
        self.assertEqual(system_check.RESULTS[0]["status"], "FAIL")
        self.assertIn("unparseable", system_check.RESULTS[0]["detail"])

    def test_missing_required_fails(self):
        with mock.patch.object(system_check, "ROOT", self.tmp):
            system_check._check_artifact("scan", "research/reports/asset_scan.json", list, 26.0, now=NOW)
        self.assertEqual(system_check.RESULTS[0]["status"], "FAIL")
        self.assertIn("missing", system_check.RESULTS[0]["detail"])

    def test_stamp_falls_back_to_mtime(self):
        self._write("research/reports/asset_scan.json", [{"pair": "BTC/USD"}], age_hours=2)
        with mock.patch.object(system_check, "ROOT", self.tmp):
            system_check._check_artifact("scan", "research/reports/asset_scan.json", list, 26.0, now=NOW)
        self.assertIn("2.0h old", system_check.RESULTS[0]["detail"])

    def test_main_exit_code_reflects_failures(self):
        with mock.patch.object(system_check, "ROOT", self.tmp), \
                mock.patch.object(system_check, "check_configs"), \
                mock.patch.object(system_check, "check_gate"), \
                mock.patch.object(system_check, "check_git"):
            code = system_check.main(["--no-git"])
        self.assertEqual(code, 1)  # empty tmp root -> missing artifacts


if __name__ == "__main__":
    sys.exit(unittest.main())

import io, os, sys, unittest, contextlib, json
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "research"))
import gate_notify as n

TOKEN = "123456789:SECRET-TOKEN-VALUE-abcdefghijklmnop"
ENV = {"TELEGRAM_BOT_TOKEN": TOKEN, "TELEGRAM_CHAT_ID": "42"}

def run(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): r = fn()
    return r, buf.getvalue()

class Notify(unittest.TestCase):
    def test_unconfigured_does_not_crash(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(n, "creds", return_value=(None, None)):
            r, out = run(lambda: n.send("x")); self.assertFalse(r); self.assertIn("not configured", out)
    def test_success_reports_message_id(self):
        resp = io.BytesIO(json.dumps({"ok": True, "result": {"message_id": 7}}).encode())
        with mock.patch.dict(os.environ, ENV), mock.patch("urllib.request.urlopen", return_value=resp):
            r, out = run(lambda: n.send("x")); self.assertTrue(r); self.assertIn("message_id 7", out)
    def test_failure_never_leaks_token(self):
        with mock.patch.dict(os.environ, ENV), mock.patch("urllib.request.urlopen", side_effect=OSError(f"https://api.telegram.org/bot{TOKEN}/sendMessage")):
            r, out = run(lambda: n.send("x")); self.assertFalse(r); self.assertNotIn(TOKEN, out)
    def test_refused_is_false(self):
        with mock.patch.dict(os.environ, ENV), mock.patch("urllib.request.urlopen", return_value=io.BytesIO(b'{"ok": false, "result": {}}')):
            self.assertFalse(run(lambda: n.send("x"))[0])
    def test_long_text_is_cut(self):
        sent = {}
        def fake(url, data, timeout): sent["d"] = data; return io.BytesIO(b'{"ok": true, "result": {"message_id": 1}}')
        with mock.patch.dict(os.environ, ENV), mock.patch("urllib.request.urlopen", side_effect=fake): run(lambda: n.send("a" * 9000))
        self.assertLess(len(sent["d"]), 4300)

if __name__ == "__main__": unittest.main()

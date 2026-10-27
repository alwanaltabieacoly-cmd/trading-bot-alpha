import json, os, subprocess, sys, tempfile, time, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "research"))
import gate_lock as L

def sh(*a, cwd): subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True)

class TradeLease(unittest.TestCase):
    """Two real clones of one bare remote stand in for the PC and GitHub."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); t = Path(self.tmp.name)
        sh("git", "init", "-q", "--bare", "-b", "main", "remote.git", cwd=t)
        self.pc, self.gh = t / "pc", t / "gh"
        sh("git", "clone", "-q", "remote.git", "pc", cwd=t)
        for c in ("user.name", "user.email"): sh("git", "config", c, "t", cwd=self.pc)
        (self.pc / "research/gate_state").mkdir(parents=True); (self.pc / "research/gate_state/x.txt").write_text("1")
        sh("git", "add", "-A", cwd=self.pc); sh("git", "commit", "-q", "-m", "init", cwd=self.pc); sh("git", "push", "-q", "origin", "HEAD:main", cwd=self.pc)
        sh("git", "clone", "-q", "remote.git", "gh", cwd=t)
        self._repo, self._file = L.REPO, L.FILE
    def tearDown(self): L.REPO, L.FILE = self._repo, self._file; self.tmp.cleanup()
    def side(self, clone): L.REPO = clone; L.FILE = clone / "research/gate_state/LOCK.json"

    def test_second_side_is_refused_while_first_holds(self):
        self.side(self.pc); owner = L.acquire("alpha-pc")
        self.side(self.gh)
        with self.assertRaises(L.LockBusy) as e: L.acquire("daily")
        self.assertIn("alpha-pc", str(e.exception))
        self.side(self.pc); L.release(owner)

    def test_release_lets_the_other_side_in(self):
        self.side(self.pc); L.release(L.acquire("alpha-pc"))
        self.side(self.gh); L.release(L.acquire("daily"))

    def test_expired_lease_is_taken_over(self):
        self.side(self.pc); L.acquire("alpha-pc", ttl=-1)    # holder crashed, lease already expired
        self.side(self.gh); L.release(L.acquire("daily"))

    def test_lost_race_is_detected(self):
        """Both read 'free'; the first push wins, the second must not believe it holds the lease."""
        self.side(self.pc); real = L._git; state = {"raced": False}
        def racing_git(*a, **k):
            if a[0] == "push" and not state["raced"]:    # before our push, the other side takes the lease
                state["raced"] = True; self.side(self.gh); L.acquire("daily"); self.side(self.pc)
            return real(*a, **k)
        L._git = racing_git
        try:
            with self.assertRaises(L.LockBusy) as e: L.acquire("alpha-pc")
            self.assertIn("daily", str(e.exception))
        finally: L._git = real

    def test_context_manager_releases_on_error(self):
        self.side(self.pc)
        with self.assertRaises(RuntimeError):
            with L.held("alpha-pc"): raise RuntimeError("boom")
        self.side(self.gh); L.release(L.acquire("daily"))

    def test_waits_for_a_short_lease(self):
        self.side(self.pc); L.acquire("alpha-pc", ttl=3)
        self.side(self.gh); real = time.sleep; L.time.sleep = lambda s: real(1)
        try: L.release(L.acquire("daily", wait_s=60))
        finally: L.time.sleep = real

if __name__ == "__main__": unittest.main()

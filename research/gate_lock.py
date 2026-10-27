"""Trade lease shared by the PC (Alpha) and GitHub (daily bot). Both trade the same testnet account and keep the trade log in git,
so only one may trade at a time. The lease is research/gate_state/LOCK.json, taken with a compare-and-swap: commit, then push.
A push Git rejects means the other side moved first, so we re-read and re-decide. A lease expires after TTL_S (a crashed holder)."""
import contextlib, json, os, subprocess, time
from pathlib import Path
import gate_analyst

TTL_S = 600
REPO = Path(__file__).resolve().parent.parent
FILE = gate_analyst.PRIVATE / "LOCK.json"

class LockBusy(Exception): pass

def _git(*a, check=True):
    r = subprocess.run(["git", "-c", "user.name=alpha-bot", "-c", "user.email=alpha-bot@users.noreply.github.com", *a], cwd=REPO,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120, env={**os.environ, "ALPHA_GIT_OK": "1"})
    if check and r.returncode: raise LockBusy(f"git {a[0]} failed: {(r.stderr or r.stdout).strip()[:200]}")
    return r

def _holder(now):
    try: lease = json.loads(FILE.read_text())
    except (FileNotFoundError, ValueError): return None
    return lease if lease["expires"] > now else None

def acquire(kind, ttl=TTL_S, wait_s=0, tries=4):
    """Take the lease; returns the owner token. Waits up to wait_s for a live holder, then raises LockBusy.
    Also raises LockBusy when Git cannot confirm we hold it."""
    owner = f"{kind}:{os.getpid()}:{int(time.time())}"; deadline = time.time() + wait_s
    while tries:
        _git("pull", "-q", "--rebase", "--autostash"); now = time.time(); lease = _holder(now)
        if lease:
            if now + 15 > deadline: raise LockBusy(f"{lease['owner']} holds the trade lease for another {int(lease['expires'] - now)} s")
            time.sleep(15); continue
        tries -= 1
        FILE.parent.mkdir(parents=True, exist_ok=True); FILE.write_text(json.dumps({"owner": owner, "expires": int(now + ttl)}))
        _git("add", "--", str(FILE)); _git("commit", "-q", "-m", f"trade lease {owner}", "--", str(FILE))
        if _git("push", "-q", "origin", "HEAD:main", check=False).returncode == 0: return owner
        _git("reset", "-q", "--mixed", "HEAD~1"); FILE.unlink(missing_ok=True); _git("checkout", "HEAD", "--", str(FILE), check=False)   # lost the race: drop only our lease commit, keep other work
    raise LockBusy("could not take the trade lease: the other side keeps moving first")

def release(owner):
    """Best effort: an unreleased lease just expires."""
    try:
        lease = json.loads(FILE.read_text())
        if lease["owner"] != owner: return
        FILE.unlink(); _git("add", "-A", "--", str(FILE)); _git("commit", "-q", "-m", f"release trade lease {owner}", "--", str(FILE))
        if _git("push", "-q", "origin", "HEAD:main", check=False).returncode:
            _git("pull", "-q", "--rebase", "--autostash", check=False); _git("push", "-q", "origin", "HEAD:main", check=False)
    except Exception: pass

@contextlib.contextmanager
def held(kind, wait_s=0):
    owner = acquire(kind, wait_s=wait_s)
    try: yield owner
    finally: release(owner)

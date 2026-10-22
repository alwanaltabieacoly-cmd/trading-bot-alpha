import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
USER_DATA = PROJECT_ROOT / "user_data"
DATA_DIR = USER_DATA / "data" / "bybit"
SENTIMENT_DB = PROJECT_ROOT / "sentiment" / "sentiment.sqlite"
FNG_CSV = USER_DATA / "external" / "fng.csv"
CONFIG_PATH = USER_DATA / "config.json"
PRIVATE_CONFIG_PATH = PROJECT_ROOT / "config.private.json"
DECISIONS_DIR = PROJECT_ROOT / "reports" / "decisions"
LATEST_DECISION_PATH = USER_DATA / "decisions" / "latest.json"

TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"]
MODELS = ["opencode/deepseek-v4.1-flash-free", "opencode/glm-5.3-flash-free"]

ANSI_RE = re.compile(
    r"\x1b\[[0-9;?]*[A-Za-z]"
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)"
    r"|\x1b[@-Z\\-_]"
)


def utc_now():
    return datetime.now(timezone.utc)


def parse_utc(value):
    if value is None:
        return utc_now()
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_utc(value):
    return parse_utc(value).isoformat()


def pair_to_base(pair):
    return str(pair).replace("/", "_").replace("-", "_").upper()


def rnd(value, nd=6):
    try:
        return round(float(value), nd)
    except (TypeError, ValueError):
        return None


def load_candles(pair, tf, asof):
    """Load cached candles for a pair/timeframe.

    Primary source: feather cache under user_data/data/bybit/ (legacy).
    Fallback: parquet cache under research/data/ (the canonical data layer
    maintained by research/data.py).  The fallback is what actually runs
    today -- the feather files were never populated.
    """
    path = DATA_DIR / f"{pair_to_base(pair)}-{tf}.feather"
    df = None
    if path.exists():
        try:
            df = pd.read_feather(path)
        except Exception:
            df = None

    if df is None or df.empty:
        try:
            from research import data as _rdata
            # The research cache stores files as <BASE>_<tf>.parquet
            # (e.g. BTC_1d.parquet), not <BASE_QUOTE>_<tf>.parquet.
            base = pair.split("/")[0].split("-")[0]
            df = _rdata.load(base, tf)
        except Exception:
            df = None

    if df is None or df.empty or "date" not in df.columns:
        return None
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], utc=True)
    asof_ts = pd.Timestamp(parse_utc(asof))
    df = df[df["date"] < asof_ts]
    if df.empty:
        return None
    return df.reset_index(drop=True)


def strip_ansi(text):
    return ANSI_RE.sub("", text or "")


def extract_json_object(text):
    if not text:
        return None
    decoder = json.JSONDecoder()
    index = 0
    while True:
        start = text.find("{", index)
        if start == -1:
            return None
        try:
            obj, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(obj, dict):
            return obj
        index = start + 1


def _opencode_exe():
    for name in ("opencode.cmd", "opencode"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _run_opencode(args, timeout):
    common_kwargs = {
        "cwd": str(PROJECT_ROOT),
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
    }
    try:
        return subprocess.run(args, **common_kwargs)
    except OSError:
        if os.name != "nt":
            raise
        compact = [a.replace("\r", " ").replace("\n", " ") for a in args]
        return subprocess.run(["cmd", "/c"] + compact, **common_kwargs)


def call_llm(prompt, timeout=300):
    exe = _opencode_exe()
    if exe is None:
        return None, "", None
    last_raw = ""
    last_model = None
    for model in MODELS:
        last_model = model
        # Windows cmd line limit (~8k chars): pass long prompts through a file.
        pdir = PROJECT_ROOT / "reports" / "decisions" / "_prompts"
        pdir.mkdir(parents=True, exist_ok=True)
        pfile = pdir / f"prompt_{os.getpid()}.md"
        pfile.write_text(prompt, encoding="utf-8")
        short = (f"Read the file {pfile.as_posix()} and follow its instructions exactly. "
                 "Do not modify any files. Reply with only the JSON object.")
        args = [exe, "run", "-m", model, short]
        try:
            proc = _run_opencode(args, timeout)
        except subprocess.TimeoutExpired:
            last_raw = ""
            continue
        except Exception:
            continue
        stdout = strip_ansi(proc.stdout or "")
        stderr = strip_ansi(proc.stderr or "")
        raw = stdout if stdout.strip() else stderr
        last_raw = raw
        obj = extract_json_object(stdout)
        if obj is None:
            obj = extract_json_object(stderr)
        if obj is not None:
            return obj, raw, model
    return None, last_raw, last_model

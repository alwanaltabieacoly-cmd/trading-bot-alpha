"""Gate bot limits in one file: config/gate.json, read by the GitHub workflow and by Alpha's MCP alike.
The file can only TIGHTEN the limits: every value must stay inside RANGES, whose edges are the approved limits. Loosening one is a code change here, reviewed by a human, not a config edit.
A missing file or key falls back to DEFAULTS (= the approved limits). A bad file is reported loudly and DEFAULTS are used, so a typo never raises risk and never stops position management."""
import json, sys
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "config" / "gate.json"
DEFAULTS = {"explore_risk_pct": 0.25, "daily_loss_pct": 1.0, "drawdown_pct": 5.0, "grace_h": 2, "explore_days": 10, "proven_days": 30,
            "risk_pct": 1.0, "max_notional_x_equity": 3.0, "max_open": 3, "max_leverage": 3, "alpha_max_trades_per_day": 2}
RANGES = {"explore_risk_pct": (0.01, 0.25), "daily_loss_pct": (0.1, 1.0), "drawdown_pct": (1.0, 5.0), "grace_h": (0, 12), "explore_days": (10, 60),
          "proven_days": (30, 365), "risk_pct": (0.01, 1.0), "max_notional_x_equity": (0.5, 3.0), "max_open": (1, 3), "max_leverage": (1, 3),
          "alpha_max_trades_per_day": (1, 2)}
INTEGERS = {"grace_h", "explore_days", "proven_days", "max_open", "max_leverage", "alpha_max_trades_per_day"}

def load(path=PATH):
    """Strict: raises SystemExit on any problem."""
    try: raw = json.loads(Path(path).read_text()) if Path(path).exists() else {}
    except ValueError as e: raise SystemExit(f"gate.json is not valid JSON: {e}")
    if not isinstance(raw, dict): raise SystemExit("gate.json must be a JSON object")
    cfg = {**DEFAULTS, **raw}
    unknown = set(cfg) - set(DEFAULTS)
    if unknown: raise SystemExit(f"gate.json: unknown keys {sorted(unknown)}")
    for k, (lo, hi) in RANGES.items():
        v = cfg[k]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not lo <= v <= hi:
            raise SystemExit(f"gate.json: {k}={v!r} is outside {lo}..{hi} (these edges are the approved limits; a config can only tighten them)")
        if k in INTEGERS and v != int(v): raise SystemExit(f"gate.json: {k}={v!r} must be a whole number")
    if cfg["explore_risk_pct"] > cfg["risk_pct"]: raise SystemExit("gate.json: explore_risk_pct must not exceed risk_pct")
    if cfg["explore_days"] >= cfg["proven_days"]: raise SystemExit("gate.json: explore_days must be below proven_days")
    return {k: int(v) if k in INTEGERS else v for k, v in cfg.items()}

def safe_load(path=PATH):
    try: return load(path)
    except SystemExit as e:
        print(f"WARNING: {e}. Using the approved defaults instead.", file=sys.stderr); return dict(DEFAULTS)

CFG = safe_load()

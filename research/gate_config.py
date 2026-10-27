"""Gate bot limits in one file: config/gate.json, read by the GitHub workflow and by Alpha's MCP alike.
A missing file or key falls back to DEFAULTS. A value outside RANGES stops the bot: a typo must not raise the risk."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "config" / "gate.json"
DEFAULTS = {"explore_risk_pct": 0.25, "daily_loss_pct": 1.0, "drawdown_pct": 5.0, "grace_h": 2, "explore_days": 10, "proven_days": 30,
            "risk_pct": 1.0, "max_notional_x_equity": 3.0, "max_open": 3, "max_leverage": 3}
RANGES = {"explore_risk_pct": (0.01, 1.0), "daily_loss_pct": (0.1, 5.0), "drawdown_pct": (1.0, 20.0), "grace_h": (0, 12), "explore_days": (1, 60),
          "proven_days": (5, 365), "risk_pct": (0.01, 2.0), "max_notional_x_equity": (0.5, 5.0), "max_open": (1, 10), "max_leverage": (1, 5)}

def load(path=PATH):
    cfg = {**DEFAULTS, **(json.loads(Path(path).read_text()) if Path(path).exists() else {})}
    unknown = set(cfg) - set(DEFAULTS)
    if unknown: raise SystemExit(f"gate.json: unknown keys {sorted(unknown)}")
    for k, (lo, hi) in RANGES.items():
        if not isinstance(cfg[k], (int, float)) or isinstance(cfg[k], bool) or not lo <= cfg[k] <= hi:
            raise SystemExit(f"gate.json: {k}={cfg[k]!r} is outside {lo}..{hi}; nothing was changed")
    if cfg["explore_risk_pct"] > cfg["risk_pct"]: raise SystemExit("gate.json: explore_risk_pct must not exceed risk_pct")
    if cfg["explore_days"] >= cfg["proven_days"]: raise SystemExit("gate.json: explore_days must be below proven_days")
    return cfg

CFG = load()

#!/usr/bin/env python3
"""Print the Markdown run summary for the strategy-research workflow.

Usage (from the workflow):
    python scripts/research_summary.py >> $GITHUB_STEP_SUMMARY

Replaces the inline `python - <<'PY'` heredoc that used to live in
.github/workflows/strategy-research.yml.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "research" / "state" / "champion.json"
DEEP = ROOT / "research" / "deep-report.json"


def main():
    # A summary step should never fail the job just because state is missing.
    if not STATE.exists():
        print("_No champion state found yet (research/state/champion.json)._")
        return 0

    state = json.loads(STATE.read_text(encoding="utf-8"))
    champ = state.get("champion") or {}
    print(f"**Champion:** `{champ.get('id', 'none')}`")
    print(f"- holdout CAGR: {champ.get('holdout_cagr', 'n/a')}%")
    print(f"- holdout max drawdown: {champ.get('holdout_dd', 'n/a')}%")
    print(f"- assets positive: {champ.get('assets_positive', 'n/a')}")
    ch = state.get("challenger")
    if ch:
        print("")
        print(f"**Challenger (awaiting paper confirmation):** `{ch.get('id')}`")
        print(f"- holdout CAGR: {ch.get('holdout_cagr', 'n/a')}%")
    print("")
    print(f"- cumulative candidates tested: {state.get('cumulative_candidates_tested', 'n/a')}")
    if DEEP.exists():
        d = json.loads(DEEP.read_text(encoding="utf-8"))
        se = d.get("selection_efficiency", {})
        print(f"- runs analysed: {d.get('n_runs', 'n/a')}")
        print(f"- selection efficiency (rank corr): {se.get('mean_rank_correlation', 'n/a')}"
              f" -> {se.get('verdict', 'n/a')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

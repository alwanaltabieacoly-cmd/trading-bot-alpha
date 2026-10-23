#!/usr/bin/env python3
"""Tune scoring weights from outcome history and print a one-line summary.

Replaces the inline `python -c "..."` that used to live in
.github/workflows/outcome.yml.
"""
import sys
from pathlib import Path

# Make `agents` importable no matter where this script is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents import feature_engine  # noqa: E402


def main():
    result, n = feature_engine.tune_weights()
    if result:
        print(f"Tuned {len(result)} weights from {n} samples")
    else:
        print(f"Not enough samples ({n}/20 needed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

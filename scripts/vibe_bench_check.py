#!/usr/bin/env python3
"""Gate for the Vibe-Trading alpha benchmark workflow.

Why this exists
---------------
`vibe-trading alpha bench` writes per-symbol data-source diagnostics to the log,
and those diagnostics contain `"status": "error"` **even when the benchmark
succeeds**. Grepping the log for "error" therefore false-fails a good run.

The trustworthy signal is the report artifact the CLI names in its output. This
gate exits 0 only when:
  1. the CLI exited 0,
  2. the log names a report_path,
  3. that report exists and is an Alpha Bench Report,
  4. the report's own summary says at least one alpha was tested.

Usage:
    python scripts/vibe_bench_check.py <cli-log-file> <cli-exit-code>
"""

import json
import os
import re
import sys

REPORT_RE = re.compile(r'"report_path"\s*:\s*"((?:[^"\\]|\\.)*)"')
TESTED_RE = re.compile(r"(\d+)\s+tested,\s*(\d+)\s+skipped")


def main(argv):
    if len(argv) < 2:
        print("usage: vibe_bench_check.py <cli-log-file> [cli-exit-code]")
        return 2
    log_path = argv[1]
    try:
        exit_code = int(argv[2]) if len(argv) > 2 else 0
    except ValueError:
        exit_code = 1

    if not os.path.isfile(log_path):
        print(f"FAIL: CLI log not found: {log_path}")
        return 1
    text = open(log_path, encoding="utf-8", errors="replace").read()
    print(f"log={log_path} bytes={len(text)} cli_exit={exit_code}")

    if exit_code != 0:
        print(f"FAIL: vibe-trading exited {exit_code}")
        return 1

    matches = REPORT_RE.findall(text)
    if not matches:
        print("FAIL: no report_path in CLI output (bench never completed)")
        return 1

    # The CLI embeds the path inside JSON, so unescape it rather than guessing.
    report = json.loads('"' + matches[-1] + '"')
    if not os.path.isfile(report):
        print(f"FAIL: report artifact missing on disk: {report}")
        return 1

    html = open(report, encoding="utf-8", errors="replace").read()
    if "Alpha Bench Report" not in html:
        print("FAIL: artifact is not an Alpha Bench Report")
        return 1

    tested = TESTED_RE.search(html)
    if not tested:
        print("FAIL: report has no 'N tested, M skipped' summary line")
        return 1

    n_tested, n_skipped = int(tested.group(1)), int(tested.group(2))
    if n_tested == 0:
        print(f"FAIL: zero alphas tested ({n_skipped} skipped)")
        return 1

    print(f"OK: {n_tested} tested, {n_skipped} skipped -> {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

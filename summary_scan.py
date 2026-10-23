"""Print top pairs from asset scan. Handles empty or missing file."""
import json, os, sys
path = 'research/reports/asset_scan.json'
if not os.path.exists(path):
    print('no asset scan yet')
    sys.exit(0)
try:
    with open(path) as f:
        results = json.load(f)
except (json.JSONDecodeError, ValueError):
    print('asset scan produced no results')
    sys.exit(0)
if not results:
    print('no pairs scanned')
    sys.exit(0)
for i, r in enumerate(results[:5]):
    print(f'{i+1}. {r["pair"]}: score={r["profit_score"]:+.4f}  momentum={r["momentum"]:+.4f}  close={r["close"]}')

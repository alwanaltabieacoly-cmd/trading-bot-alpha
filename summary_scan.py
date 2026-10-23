"""Print top pairs from asset scan."""
import json
with open('research/reports/asset_scan.json') as f:
    results = json.load(f)
for i, r in enumerate(results[:5]):
    print(f'{i+1}. {r["pair"]}: score={r["profit_score"]:+.4f}  momentum={r["momentum"]:+.4f}  close={r["close"]}')

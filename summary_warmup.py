"""Print warmup summary from the latest report."""
import json, glob, os, sys
wdir = 'research/reports/warmup'
files = sorted(glob.glob(f'{wdir}/*.json'), reverse=True)
if not files:
    print('no reports')
    sys.exit(0)
with open(files[0]) as f:
    data = json.load(f)
for pair, r in data.items():
    regime = r.get('regime') or 'N/A'
    tf = r.get('regime_tf') or ''
    fng = (r.get('fng') or {}).get('value', 'N/A')
    print(f'- **{pair}**: {r["verdict"]} (score={r["score"]})')
    print(f'  regime={regime} {tf}  F&G={fng}')
    for b in r.get('blockers', []):
        print(f'  BLOCK: {b}')

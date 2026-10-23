"""Print outcome summary from the outcome log."""
import json
log = 'research/reports/warmup/outcome_log.jsonl'
try:
    with open(log) as f:
        lines = f.readlines()
    if not lines:
        print('no outcomes yet')
        exit(0)
    latest = json.loads(lines[-1])
    outs = latest['outcomes']
    correct = sum(1 for o in outs if o['result']=='CORRECT')
    wrong = sum(1 for o in outs if o['result']=='WRONG')
    missed = sum(1 for o in outs if o['result']=='MISSED')
    total = len(outs)
    print(f'**Today**: {correct} correct, {wrong} wrong, {missed} missed ({correct/total*100:.0f}%)')
    for o in outs:
        chg = o.get('price_change_1h_pct') or o.get('price_change_1d_pct')
        chg_str = f'{chg:+.3f}%' if chg is not None else 'N/A'
        print(f'- {o["pair"]}: {o["verdict"]} -> {o["result"]} ({chg_str})')
except FileNotFoundError:
    print('no outcome log yet')

#!/usr/bin/env python3
"""Fetch real AAPL data and backtest the two equity scalp strategies."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from research import config, data, engine, strategies

def run(timeframes):
    print(f"Fetching AAPL for {timeframes} ...")
    frames = {}
    caps = {"1m": 6, "5m": 55, "15m": 55, "1h": 700, "1d": 1600}
    for tf in timeframes:
        try:
            df = data.update_asset("AAPL", tf, days_back=caps.get(tf, 800))
            if df is not None and len(df):
                frames[tf] = df
                print(f"  {tf}: {len(df)} bars  {df['date'].iloc[0]} -> {df['date'].iloc[-1]}")
            else:
                print(f"  {tf}: no data")
        except Exception as e:
            print(f"  {tf}: FAILED {type(e).__name__}: {e}")
    if not frames:
        print("No data fetched. Aborting.")
        return 1
    print("\nExpanding candidates ...")
    cands = strategies.expand()
    print(f"  {len(cands)} candidates")
    print("\nBacktesting ...")
    results = []
    for cid, params, fn, family, desc in cands:
        if not cid.startswith("aapl_scalp"):
            continue
        for tf, df in frames.items():
            try:
                signal = fn(df, **params)
                m = engine.evaluate(df, signal, tf, symbol="AAPL")
                row = {"cid": cid, "family": family, "params": params, "tf": tf}
                row.update(m)
                results.append(row)
                print(f"  {cid:26s} {tf:3s}  CAGR={m['cagr_pct']:7.2f}%  "
                      f"Sharpe={m['sharpe']:6.3f}  MaxDD={m['max_drawdown_pct']:7.2f}%  "
                      f"trades={m['trades']:4d}  exposure={m['exposure_pct']:5.1f}%")
            except Exception as e:
                print(f"  {cid} {tf}: FAILED {type(e).__name__}: {e}")
    out = os.path.join(config.REPORT_DIR, "aapl_backtest.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nWrote {out}")
    if results:
        best = max(results, key=lambda r: r.get("cagr_pct", -9999))
        bh = results[0].get("buy_hold", {})
        print(f"\nBest:  {best['cid']} {best['tf']}  CAGR={best['cagr_pct']:.2f}%  "
              f"Sharpe={best['sharpe']:.3f}  MaxDD={best['max_drawdown_pct']:.2f}%")
        print(f"B&H:   CAGR={bh.get('cagr_pct')}%  MaxDD={bh.get('max_drawdown_pct')}%")
    return 0

if __name__ == "__main__":
    tfs = ["1d", "1h"]
    if "--full" in sys.argv:
        tfs = ["1m", "5m", "15m", "1h", "1d"]
    sys.exit(run(tfs))
"""Daily research runner.

This is the part that runs on its own, every day, with the PC off.

What it does:
  1. Fetches fresh Bybit candles and updates the local cache.
  2. Runs EVERY candidate in the strategy registry over the TRAIN window.
  3. Filters candidates by the promotion rules.
  4. Scores survivors on the HOLDOUT window, which the search never saw.
  5. Applies the Deflated Sharpe correction for the number of trials.
  6. Compares the best survivor to the current champion.
  7. Writes a dated report and updates the champion state.

What it deliberately does NOT do:
  - It never picks a strategy using holdout data.
  - It never promotes on backtest alone. A challenger that wins becomes a
    CANDIDATE and must then prove itself in live paper trading before it
    becomes the champion.
  - It never touches real money.
"""
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import config, data, engine, strategies, validate


# --------------------------------------------------------------------------
# champion state
# --------------------------------------------------------------------------


def load_state():
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "champion": None,
        "challenger": None,
        "history": [],
        "created": config.now_iso(),
    }


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# --------------------------------------------------------------------------
# evaluation
# --------------------------------------------------------------------------


def eval_candidate(cid, params, fn, frames, train_end, holdout_start):
    """Evaluate one candidate across all assets and timeframes.

    frames: list of (asset, timeframe, df)
    Returns an aggregate dict or None if the candidate blew up.
    """
    train_masks = {}
    hold_masks = {}
    per_asset = {}
    n_obs = 0
    pooled_train = []
    pooled_hold = []

    try:
        for asset, tf, df in frames:
            dates = df["date"]
            train_m = engine.date_mask(dates, end=train_end)
            hold_m = engine.date_mask(dates, start=holdout_start)
            if train_m.sum() < 60 or hold_m.sum() < 20:
                continue

            signal = fn(df, **params)
            if len(signal) != len(df):
                signal = pd.Series(np.asarray(signal, dtype=bool), index=df.index)

            net, pos, _ = engine.backtest(df, signal)
            tr = engine.evaluate(df, signal, tf, mask=train_m, symbol=asset)
            hd = engine.evaluate(df, signal, tf, mask=hold_m, symbol=asset)
            per_asset[f"{asset}_{tf}"] = {"train": tr, "holdout": hd}
            n_obs = max(n_obs, tr["bars"])

            # Pooled portfolio: equal weight across assets on the daily
            # timeframe. This is the series the headline Sharpe and the
            # Deflated Sharpe are computed from.
            if tf == "1d":
                s = pd.Series(net, index=pd.DatetimeIndex(dates))
                pooled_train.append(s[train_m])
                pooled_hold.append(s[hold_m])
    except Exception as e:
        return {
            "id": cid,
            "params": params,
            "error": f"{type(e).__name__}: {e}",
            "per_asset": {},
        }

    if not per_asset:
        return None

    # Aggregate = equal weight across assets (no asset gets to dominate)
    def agg(section, key):
        vals = [
            v[section][key]
            for v in per_asset.values()
            if section in v and v[section].get(key) is not None
            and np.isfinite(v[section][key])
        ]
        return float(np.mean(vals)) if vals else float("nan")

    train_cagr = agg("train", "cagr_pct")
    hold_cagr = agg("holdout", "cagr_pct")
    train_dd = agg("train", "max_drawdown_pct")
    hold_dd = agg("holdout", "max_drawdown_pct")
    hold_sharpe = agg("holdout", "sharpe")
    assets_positive = sum(
        1 for v in per_asset.values()
        if v["holdout"].get("cagr_pct") is not None and v["holdout"]["cagr_pct"] > 0
    )

    # Pooled portfolio metrics (daily, equal weight across assets)
    pooled = {}
    if pooled_train:
        pt = pd.concat(pooled_train, axis=1).mean(axis=1)
        pooled["train"] = engine.metrics(pt.to_numpy(), config.PERIODS_PER_YEAR["1d"])
        pooled["train"]["bars"] = int(len(pt))
    if pooled_hold:
        ph = pd.concat(pooled_hold, axis=1).mean(axis=1)
        pooled["holdout"] = engine.metrics(ph.to_numpy(), config.PERIODS_PER_YEAR["1d"])
        pooled["holdout"]["bars"] = int(len(ph))

    return {
        "id": cid,
        "params": params,
        "train_cagr": round(train_cagr, 3),
        "holdout_cagr": round(hold_cagr, 3),
        "train_dd": round(train_dd, 3),
        "holdout_dd": round(hold_dd, 3),
        "holdout_sharpe": round(hold_sharpe, 3) if np.isfinite(hold_sharpe) else None,
        "pooled": pooled,
        "assets_positive": assets_positive,
        "assets_tested": len(per_asset),
        "n_obs": n_obs,
        "per_asset": per_asset,
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


EXIT_SKIPPED = 10


def main(argv=None):
    argv = argv or sys.argv[1:]
    skip_fetch = "--no-fetch" in argv

    min_interval_hours = 0.0
    for a in argv:
        if a.startswith("--min-interval-hours="):
            min_interval_hours = float(a.split("=", 1)[1])

    t_start = time.time()
    print("=" * 78)
    print(f"DAILY RESEARCH RUN - {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print("=" * 78)

    # 0. gate
    #
    # GitHub's scheduler is best-effort: a scheduled run can be delayed by
    # an hour or skipped entirely. So the workflow ticks hourly and this
    # gate decides whether a run is actually due. A missed slot is picked
    # up by the next tick instead of being lost for four hours.
    if min_interval_hours > 0:
        st = load_state()
        last = st.get("last_run")
        if last:
            try:
                last_dt = datetime.fromisoformat(last)
                age_h = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600.0
            except Exception:
                age_h = 999.0
            if age_h < min_interval_hours:
                print(f"\n[0/6] skipping: last run was {age_h:.2f}h ago, "
                      f"minimum interval is {min_interval_hours}h")
                print("       (the next hourly tick will pick this up if needed)")
                return EXIT_SKIPPED
            print(f"\n[0/6] due: last run was {age_h:.2f}h ago "
                  f"(minimum {min_interval_hours}h)")

    # 1. data
    if not skip_fetch:
        print("\n[1/6] fetching market data")
        data.update_all()
    else:
        print("\n[1/6] using cached data (--no-fetch)")

    # Crypto frames
    frames = []
    for a in config.ASSETS:
        for tf in config.TIMEFRAMES:
            df = data.load(a, tf)
            if df is None or len(df) < 300:
                print(f"  WARNING: no usable data for {a} {tf}")
                continue
            frames.append((a, tf, df))
    # Equity frames (TradingView integration)
    for a in config.EQUITY_ASSETS:
        for tf in config.EQUITY_TIMEFRAMES:
            df = data.load(a, tf)
            if df is None or len(df) < 30:
                print(f"  WARNING: no usable data for {a} {tf}")
                continue
            frames.append((a, tf, df))
    if not frames:
        print("ERROR: no data available. Run once without --no-fetch.")
        return 2
    print(f"  loaded {len(frames)} asset/timeframe series")

    # 2. evolve: let the accumulated evidence shape this run's search space
    from . import evolve

    print("\n[2/6] evolving the search space from accumulated evidence")
    ev_df = evolve.load_history()
    ev_state = evolve.load_state()
    ev_decision = evolve.decide(ev_df, ev_state)
    ev_saved = evolve.apply(ev_decision, ev_state)
    retired = ev_saved.get("retired_families", [])
    for r in ev_decision.get("reasons", []):
        print(f"  {r}")
    print(f"  retired families: {retired or 'none'}")

    # 3. expand candidates
    train_end, holdout_start = config.split_dates()
    candidates = strategies.expand()
    print(f"\n[3/6] evaluating {len(candidates)} candidates on the TRAIN window")
    print(f"        train ends {train_end}, holdout starts {holdout_start} "
          f"(rolling {config.HOLDOUT_DAYS}-day holdout)")

    results = []
    for i, (cid, params, fn, family, desc) in enumerate(candidates):
        r = eval_candidate(cid, params, fn, frames, train_end, holdout_start)
        if r and "error" not in r:
            r["family"] = family
            results.append(r)
        if (i + 1) % 25 == 0:
            print(f"        {i + 1}/{len(candidates)}", flush=True)

    n_trials = len(results)
    print(f"  {n_trials} candidates evaluated")

    # 3. apply the deflated Sharpe correction for how many things we tried
    print("\n[4/6] applying Deflated Sharpe correction "
          f"(n_trials={n_trials})")
    for r in results:
        # Headline DSR: computed on the POOLED equal-weight daily portfolio
        # over the TRAIN window (where the selection happened), so the trial
        # count correction applies to the actual selection process.
        pooled = r.get("pooled", {})
        ptr = pooled.get("train", {})
        sharpe = ptr.get("sharpe")
        nb = ptr.get("bars", 0)
        if sharpe is None or not np.isfinite(sharpe) or nb <= 2:
            r["dsr"] = 0.0
        else:
            r["dsr"] = round(validate.deflated_sharpe(
                sharpe,
                n_trials=n_trials,
                n_obs=nb,
                periods_per_year=config.PERIODS_PER_YEAR["1d"],
            ), 4)

        # Per-series DSR kept as a diagnostic (the weakest series decides)
        dsrs = {}
        for key, v in r["per_asset"].items():
            tf = key.split("_")[-1]
            ppy = config.PERIODS_PER_YEAR.get(tf, 365)
            sh = v["train"].get("sharpe")
            nbb = v["train"].get("bars", 0)
            if sh is None or not np.isfinite(sh) or nbb <= 2:
                continue
            dsrs[key] = round(validate.deflated_sharpe(
                sh, n_trials=n_trials, n_obs=nbb, periods_per_year=ppy), 4)
        r["dsr_by_series"] = dsrs
        r["dsr_min_series"] = round(min(dsrs.values()), 4) if dsrs else 0.0

        ok_basic, reasons_basic = validate.passes_basic(r)
        ok_gate, reasons_gate = validate.passes_gate(r)
        r["passes_basic"] = ok_basic
        r["passes_gate"] = ok_gate
        r["gate_failures"] = reasons_gate

    basic = [r for r in results if r["passes_basic"]]
    basic.sort(key=lambda r: r["holdout_cagr"], reverse=True)
    survivors = [r for r in results if r["passes_gate"]]
    survivors.sort(key=lambda r: r["holdout_cagr"], reverse=True)
    print(f"  {len(basic)} candidates passed the basic rules")
    print(f"  {len(survivors)} candidates passed every promotion rule")

    # 4. champion comparison
    state = load_state()
    champ = state.get("champion")
    champ_hold = None
    if champ:
        # The champion is re-evaluated on EVERY run, because the holdout
        # window rolls forward. Comparing a fresh candidate against a
        # stored champion number would compare two different windows.
        champ_row = next((r for r in results if r["id"] == champ.get("id")), None)
        if champ_row:
            champ_hold = champ_row["holdout_cagr"]
            champ["holdout_cagr"] = champ_hold
            champ["holdout_dd"] = champ_row["holdout_dd"]
            champ["train_cagr"] = champ_row["train_cagr"]
            champ["dsr"] = champ_row["dsr"]
            champ["assets_positive"] = champ_row["assets_positive"]
            champ["last_evaluated"] = config.now_iso()
        else:
            champ_hold = champ.get("holdout_cagr")
        print(f"\n[5/6] current champion: {champ.get('id')} "
              f"(holdout CAGR {champ_hold:.1f}% on the current window)")
    else:
        print("\n[5/6] no champion yet")

    best = survivors[0] if survivors else None
    promoted = False
    bootstrapped = False

    if champ is None:
        # Bootstrap: pick the best candidate that clears the basic rules so
        # the system has something to beat. It is labelled backtest-only -
        # it still has to confirm itself in live paper trading.
        if basic:
            pick = basic[0]
            state["champion"] = {
                "id": pick["id"],
                "params": pick["params"],
                "train_cagr": pick["train_cagr"],
                "holdout_cagr": pick["holdout_cagr"],
                "train_dd": pick["train_dd"],
                "holdout_dd": pick["holdout_dd"],
                "dsr": pick["dsr"],
                "assets_positive": pick["assets_positive"],
                "promoted_at": config.now_iso(),
                "status": "initial_backtest_only",
                "note": "Chosen as the starting champion from the first run. "
                        "Must confirm itself in live paper trading.",
            }
            bootstrapped = True
            print(f"  bootstrapped initial champion: {pick['id']} "
                  f"(holdout CAGR {pick['holdout_cagr']:.1f}%)")
        else:
            print("  no candidate cleared even the basic rules")
    elif best:
        if validate.beats_champion(best["holdout_cagr"], champ_hold):
            state["challenger"] = {
                "id": best["id"],
                "params": best["params"],
                "train_cagr": best["train_cagr"],
                "holdout_cagr": best["holdout_cagr"],
                "holdout_dd": best["holdout_dd"],
                "dsr": best["dsr"],
                "assets_positive": best["assets_positive"],
                "promoted_at": config.now_iso(),
                "status": "awaiting_paper_confirmation",
                "note": "Backtest win only. Must confirm with live paper trading "
                        "before it becomes the champion.",
            }
            promoted = True
            print(f"  challenger {best['id']} beats the champion "
                  f"({best['holdout_cagr']:.1f}% vs {champ_hold:.1f}%)")
        else:
            print("  no candidate beats the champion's holdout CAGR")
    else:
        print("  no candidate cleared the promotion rules")

    # 5. report
    print("\n[6/6] writing report")
    results_sorted = sorted(results, key=lambda r: r["holdout_cagr"], reverse=True)
    report = {
        "run_at": config.now_iso(),
        "duration_sec": round(time.time() - t_start, 1),
        "config": {
            "assets": config.ASSETS,
            "timeframes": config.TIMEFRAMES,
            "equity_assets": config.EQUITY_ASSETS,
            "equity_timeframes": config.EQUITY_TIMEFRAMES,
            "fee_per_side": config.FEE_PER_SIDE,
            "slippage_per_side": config.SLIPPAGE_PER_SIDE,
            "train_end": train_end,
            "holdout_start": holdout_start,
            "holdout_days": config.HOLDOUT_DAYS,
            "min_train_cagr": config.MIN_TRAIN_CAGR_PCT,
            "min_holdout_cagr": config.MIN_HOLDOUT_CAGR_PCT,
            "min_asset_consistency": config.MIN_ASSET_CONSISTENCY,
            "min_deflated_sharpe": config.MIN_DEFLATED_SHARPE,
            "n_trials": n_trials,
        },
        "champion": state.get("champion"),
        "n_candidates": n_trials,
        "evolution": {
            "retired_families": retired,
            "reasons": ev_decision.get("reasons", []),
            "explore_next": ev_decision.get("explore_next", [])[:5],
            "n_runs_of_evidence": ev_decision.get("n_runs", 0),
        },
        "n_basic": len(basic),
        "n_survivors": len(survivors),
        "challenger_proposed": promoted,
        "champion_bootstrapped": bootstrapped,
        "top_basic": [
            {
                "id": r["id"],
                "params": r["params"],
                "train_cagr": r["train_cagr"],
                "holdout_cagr": r["holdout_cagr"],
                "train_dd": r["train_dd"],
                "holdout_dd": r["holdout_dd"],
                "dsr": r["dsr"],
                "dsr_min_series": r.get("dsr_min_series"),
                "assets_positive": r["assets_positive"],
                "gate_failures": r["gate_failures"],
            }
            for r in basic[:10]
        ],
        "top_survivors": [
            {
                "id": r["id"],
                "params": r["params"],
                "train_cagr": r["train_cagr"],
                "holdout_cagr": r["holdout_cagr"],
                "train_dd": r["train_dd"],
                "holdout_dd": r["holdout_dd"],
                "holdout_sharpe": r["holdout_sharpe"],
                "dsr": round(r["dsr"], 4),
                "assets_positive": r["assets_positive"],
            }
            for r in survivors[:10]
        ],
        "best_overall_by_holdout": (
            {
                "id": results_sorted[0]["id"],
                "train_cagr": results_sorted[0]["train_cagr"],
                "holdout_cagr": results_sorted[0]["holdout_cagr"],
                "dsr": round(results_sorted[0]["dsr"], 4),
                "passed_gate": results_sorted[0]["passes_gate"],
            }
            if results_sorted else None
        ),
    }

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    json_path = os.path.join(config.REPORT_DIR, f"{stamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md_path = os.path.join(config.REPORT_DIR, f"{stamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(report, results))

    # Cumulative count of every candidate ever evaluated. The Deflated
    # Sharpe correction inside a single run only accounts for the trials in
    # THAT run. This counter is the honest record of how many times the
    # whole search has been repeated, which is the real degree of freedom
    # a researcher accumulates over time.
    cumulative = int(state.get("cumulative_candidates_tested", 0)) + n_trials
    state["cumulative_candidates_tested"] = cumulative
    report["cumulative_candidates_tested"] = cumulative

    state["last_run"] = config.now_iso()
    state["last_run_report"] = os.path.basename(json_path)
    state["history"] = (state.get("history", []) + [{
        "at": config.now_iso(),
        "n_candidates": n_trials,
        "n_survivors": len(survivors),
        "best_id": report["best_overall_by_holdout"]["id"] if report["best_overall_by_holdout"] else None,
        "best_holdout_cagr": report["best_overall_by_holdout"]["holdout_cagr"] if report["best_overall_by_holdout"] else None,
        "challenger_proposed": promoted,
        "train_end": train_end,
        "holdout_start": holdout_start,
    }])[-400:]
    save_state(state)

    # Per-candidate history. This is what turns a pile of isolated runs into
    # evidence: a strategy that is good in one window is a fluke, a strategy
    # that is good in every window is a candidate for the champion.
    write_history(results, run_at=config.now_iso(), train_end=train_end,
                  holdout_start=holdout_start)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(report, results))

    print(f"\nreport: {json_path}")
    print(f"        {md_path}")
    print(f"done in {report['duration_sec']}s")
    return 0


def write_history(results, run_at, train_end, holdout_start):
    """Append one row per candidate to research/history.csv.

    Over many runs this becomes the real evidence base: which strategies
    are good again and again, and which ones only ever looked good once.
    """
    import csv

    path = os.path.join(config.PROJECT_ROOT, "research", "history.csv")
    fields = [
        "run_at", "candidate_id", "family",
        "train_cagr", "holdout_cagr", "train_dd", "holdout_dd",
        "holdout_sharpe", "dsr", "assets_positive", "assets_tested",
        "passes_basic", "passes_gate",
        "train_end", "holdout_start",
    ]
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            w.writeheader()
        for r in results:
            w.writerow({
                "run_at": run_at,
                "candidate_id": r["id"],
                "family": r.get("family") or r["id"].split("_")[0],
                "train_cagr": r["train_cagr"],
                "holdout_cagr": r["holdout_cagr"],
                "train_dd": r["train_dd"],
                "holdout_dd": r["holdout_dd"],
                "holdout_sharpe": r.get("holdout_sharpe"),
                "dsr": r.get("dsr"),
                "assets_positive": r["assets_positive"],
                "assets_tested": r["assets_tested"],
                "passes_basic": r.get("passes_basic"),
                "passes_gate": r.get("passes_gate"),
                "train_end": train_end,
                "holdout_start": holdout_start,
            })
    return path


def render_markdown(report, results):
    lines = []
    lines.append(f"# Daily research report - {report['run_at']}")
    lines.append("")
    c = report["config"]
    lines.append(f"- Candidates tested: **{c['n_trials']}**")
    lines.append(f"- Passed every promotion rule: **{report['n_survivors']}**")
    lines.append(f"- Costs modelled: {c['fee_per_side'] * 100:.2f}% fee + "
                 f"{c['slippage_per_side'] * 100:.2f}% slippage per side")
    lines.append(f"- Train window: ... -> {c['train_end']}  |  "
                 f"Holdout window: {c['holdout_start']} -> now "
                 f"(rolling {c.get('holdout_days', 180)}-day holdout)")
    lines.append(f"- Cumulative candidates ever tested: "
                 f"{report.get('cumulative_candidates_tested', c['n_trials'])}")
    lines.append("")

    champ = report.get("champion")
    lines.append("## Champion")
    if champ:
        lines.append(f"`{champ['id']}` - holdout CAGR {champ['holdout_cagr']:.1f}%, "
                     f"holdout maxDD {champ['holdout_dd']:.1f}%, "
                     f"{champ.get('assets_positive')} assets positive")
    else:
        lines.append("None yet.")
    lines.append("")

    lines.append("## Survivors (cleared every rule)")
    if not report["top_survivors"]:
        lines.append("None today.")
    else:
        lines.append("| strategy | train CAGR | holdout CAGR | holdout DD | Sharpe | DSR | assets+ |")
        lines.append("|---|---|---|---|---|---|---|")
        for s in report["top_survivors"]:
            lines.append(
                f"| `{s['id']}` | {s['train_cagr']:.1f}% | {s['holdout_cagr']:.1f}% | "
                f"{s['holdout_dd']:.1f}% | {s['holdout_sharpe']} | {s['dsr']:.3f} | "
                f"{s['assets_positive']} |"
            )
    lines.append("")

    lines.append("## Basic-rule passers (profitable, consistent - DSR not yet high enough)")
    if not report.get("top_basic"):
        lines.append("None today.")
    else:
        lines.append("| strategy | train CAGR | holdout CAGR | holdout DD | DSR | assets+ | blocked by |")
        lines.append("|---|---|---|---|---|---|---|")
        for s in report["top_basic"]:
            lines.append(
                f"| `{s['id']}` | {s['train_cagr']:.1f}% | {s['holdout_cagr']:.1f}% | "
                f"{s['holdout_dd']:.1f}% | {s['dsr']:.3f} | {s['assets_positive']} | "
                f"{'; '.join(s['gate_failures'][:1])} |"
            )
    lines.append("")

    best = report.get("best_overall_by_holdout")
    lines.append("## Best by holdout, regardless of gate")
    if best:
        lines.append(f"`{best['id']}` - holdout CAGR {best['holdout_cagr']:.1f}%, "
                     f"DSR {best['dsr']:.3f}, passed gate: {best['passed_gate']}")
        if not best["passed_gate"]:
            lines.append("")
            lines.append("> This one did NOT clear the promotion rules. It is shown for "
                         "transparency only - the runner will not act on it.")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    ev = report.get("evolution") or {}
    if ev.get("retired_families"):
        lines.append(f"- **Retired this run:** {', '.join('`'+f+'`' for f in ev['retired_families'])} "
                     "- families whose every variant lost money on the untouched window.")
    if ev.get("explore_next"):
        lines.append("- **Families flagged for more exploration:** "
                     + ", ".join(f"`{e['family']}`" for e in ev["explore_next"]))
    lines.append("- The holdout window is never used to select between candidates.")
    lines.append("- The Deflated Sharpe correction accounts for how many candidates "
                 "were tried, so a lucky winner cannot pass by chance.")
    lines.append("- Nothing here promotes a strategy on backtest alone. A challenger "
                 "must also confirm itself in live paper trading.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

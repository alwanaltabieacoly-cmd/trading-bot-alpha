"""Shared configuration for the research harness.

The guardrails live here. Every number that decides whether a strategy is
allowed to promote is explicit, so a reader can audit the whole thing.
"""
from datetime import datetime, timezone

# --- market ---------------------------------------------------------------
EXCHANGE = "bybit"
ASSETS = ["BTC", "ETH", "SOL", "BNB", "XRP"]

# --- equity assets (TradingView integration) ------------------------------
# These are fetched from Yahoo Finance (free, no API key) and backtested
# alongside the crypto universe. The 1m AAPL scalp is the bridge between
# the TradingView chart work and the GitHub research harness.
EQUITY_ASSETS = ["AAPL"]
EQUITY_TIMEFRAMES = ["1m", "5m", "15m", "1h", "1d"]

# --- costs (equity, US market standard) -----------------------------------
# AAPL on 1m: $0.01-$0.02 spread, ~$0.005 per share commission.
# Modelled conservatively as 0.05% per side (spread + commission + slippage).
EQUITY_COST_PER_SIDE = 0.0005

# --- periods --------------------------------------------------------------
# 1m intraday has 390 trading bars/day x 252 trading days.
PERIODS_PER_YEAR_EQUITY = {
    "1m": 390 * 252,
    "5m": 78 * 252,
    "15m": 26 * 252,
    "1h": 6.5 * 252,
    "1d": 252,
}
TIMEFRAMES = ["1d", "4h"]

# --- costs (Bybit spot standard tier) -------------------------------------
FEE_PER_SIDE = 0.001        # taker fee
SLIPPAGE_PER_SIDE = 0.0002  # small retail order allowance
COST_PER_SIDE = FEE_PER_SIDE + SLIPPAGE_PER_SIDE

# --- periods --------------------------------------------------------------
PERIODS_PER_YEAR = {"1d": 365, "4h": 6 * 365, "1h": 24 * 365, "15m": 96 * 365}

# Rolling walk-forward split.
#
# The holdout is ALWAYS the most recent HOLDOUT_DAYS of market data, and it
# is NEVER used to select between candidates. Because the window rolls
# forward on every run, each run tests the strategies against a stretch of
# data that was genuinely unseen when the selection was made.
#
# That matters because the harness runs every few hours: with a fixed
# holdout, a strategy could slowly "learn" the holdout just by being
# looked at repeatedly. With a rolling one, the holdout keeps moving.
HOLDOUT_DAYS = 180


def split_dates(today=None):
    """Return (train_end, holdout_start) as ISO date strings.

    train_end    : last day usable for SELECTION
    holdout_start: first day of the untouched evaluation window
    """
    import datetime as dt

    today = today or dt.datetime.now(dt.timezone.utc)
    holdout_start = (today.date() - dt.timedelta(days=HOLDOUT_DAYS))
    train_end = holdout_start - dt.timedelta(days=1)
    return train_end.isoformat(), holdout_start.isoformat()


TRAIN_END, HOLDOUT_START = split_dates()

# --- promotion rules ------------------------------------------------------
# A challenger must clear ALL of these to even be considered.
MIN_TRAIN_CAGR_PCT = 5.0          # must actually make money on train
MIN_HOLDOUT_CAGR_PCT = 0.0        # must not lose money on the untouched window
MIN_ASSET_CONSISTENCY = 3        # must work on at least N of the assets
MAX_DEFLATED_SHARPE_TRIALS = 200  # multiple-testing correction budget
MIN_DEFLATED_SHARPE = 0.95        # DSR confidence level required

# A challenger must ALSO beat the current champion by this margin on holdout.
MIN_IMPROVEMENT_OVER_CHAMPION_PCT = 2.0

# --- paths ----------------------------------------------------------------
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "research", "data")
REPORT_DIR = os.path.join(PROJECT_ROOT, "research", "reports")
STATE_DIR = os.path.join(PROJECT_ROOT, "research", "state")
STATE_FILE = os.path.join(STATE_DIR, "champion.json")
LOG_DIR = os.path.join(PROJECT_ROOT, "research", "logs")

for _d in (DATA_DIR, REPORT_DIR, STATE_DIR, LOG_DIR):
    os.makedirs(_d, exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def cost_per_side(symbol):
    """Return the per-side cost for a given symbol.
    Crypto uses Bybit's taker fee + slippage. Equities use a spread +
    commission model appropriate to the timeframe.
    """
    if symbol in EQUITY_ASSETS:
        return EQUITY_COST_PER_SIDE
    return COST_PER_SIDE


def periods_per_year(symbol, timeframe):
    """Pick the right bar count for the asset class."""
    if symbol in EQUITY_ASSETS:
        return PERIODS_PER_YEAR_EQUITY.get(timeframe, 252)
    return PERIODS_PER_YEAR.get(timeframe, 365)
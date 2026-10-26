# Gate.io — platform guide for Alpha (public-safe: no account data)
Verified 2026-10-26 against api.gateio.ws/api/v4. "Unverified" marks anything not tested.

## 1. Account areas and where the data lives
| Area | What it is | API (GET) | Notes |
|---|---|---|---|
| Spot | Coin-for-coin trading, 0.10% maker/taker at VIP0 | `/spot/accounts`, `/spot/open_orders`, `/spot/my_trades`, `/spot/account_book` | `my_trades` and `account_book` need `from`/`to` windows of <=30 days; loop windows to go back further |
| USDT perpetual futures | Leveraged, long/short, fees 0.02% maker / 0.05% taker | `/futures/usdt/accounts`, `/positions`, `/my_trades`, `/account_book` | Account is created only after a transfer in; `futures/btc` and `delivery` return USER_NOT_FOUND until then |
| Unified account | Cross-margin across products | `/unified/accounts` | 403 "Please open the Unified Account" if not opened |
| Wallet | Deposits, withdrawals, small-balance conversion | `/wallet/deposits`, `/withdrawals`, `/small_balance`, `/saved_address` | Windows of <=30 days |
| Flash swap | One-click coin conversion | `/flash_swap/orders` | Shows as `cv_sell`/`cv_buy` in the spot ledger |
| Earn / staking / options / alpha / tradfi | Yield, options, on-chain "alpha" tokens, CFD | `/earn/...`, `/options/accounts`, `/alpha/...`, `/tradfi/...` | tradfi returns USER_NOT_EXIST if never opened |

## 2. Ledger vocabulary (spot `account_book.type`)
`new_order` (quote spent), `order_fill` (base received), `order_fee`, `deposit`, `cv_sell`/`cv_buy` (flash swap), `perp_in`/`perp_out` (transfer to/from futures), `unknown` (internal/transfer legs). Spot fees on buys are taken **from the coin bought** (buy 1946 CENT -> receive 1944.054).

## 3. Market data (public, no key)
- Spot: `/spot/tickers`, `/spot/order_book?currency_pair=X_USDT&limit=N`, `/spot/candlesticks?currency_pair=&interval=1m|1d&limit=` (rows: t, quote_vol, close, high, low, open, base_vol, closed).
- Futures: `/futures/usdt/tickers` (has funding_rate), `/futures/usdt/contracts/{c}`, `/futures/usdt/candlesticks`.
- Futures perps also exist for gold (XAU), silver (XAG), and stocks (MU, INTC), so gold can be traded and logged here.
- Pair rules: `/spot/currency_pairs/{pair}` -> `min_quote_amount` (min order value in USDT), `min_base_amount`, `precision`, `buy_start` (listing time), `trade_status`.

## 4. API quirks we hit
- Futures candles: `limit` cannot be combined with `to`/`from`; use `from`+`to` (<=2000 bars). Only the **latest 10,000 1m bars** (~6.9 days) are served.
- Public endpoints return 200 with a User-Agent header; keep one set.
- Rate limits: public 200 req/10 s per endpoint per IP; spot orders 10/s; futures orders 100/s.
- Auth: `KEY`, `Timestamp`, `SIGN = HMAC_SHA512(secret, METHOD\n/api/v4/path\nquery\nSHA512(body)\nTimestamp)`.
- `/account/main_keys` lists every permission of the calling key; `ip_whitelist: []` means no IP restriction.

## 5. Microstructure facts that matter for trading
- Round-trip cost: spot 0.20%; futures 0.04% (maker/maker) to 0.10% (taker/taker); funding ~0.005%/8 h on majors.
- Low-cap listings: new pairs often spike on listing day then bleed for days; thin books (a $2-5k position can move price).
- `min_quote_amount` (commonly 3 USDT) blocks selling positions worth less than that with a normal order. A small position can get stuck.

## 6. Files in this repo
- `gate_auth.py` signed read-only client (blocks non-GET unless `ALPHA_GATE_TRADE=1`); `audit`, `check`, `set`.
- `gate_account_dump.py` read-only dump of every account area to `data/gate_account/` (gitignored).
- `gate_logger.py` 5 s order-book + 1m candle logger (BTC/ETH/SOL/XRP).
- `gate_signal_probe.py`, `crypto_scan.py`, `crypto_rule_check.py` research probes. Results: `MARKET_RESEARCH.md` sections 15-17, `CRYPTO_SCAN.md`.
- Personal account analysis lives in `research/private/GATE_ACCOUNT.md` (local only, gitignored, repo is public).

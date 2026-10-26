"""Read-only dump of every Gate account area reachable with the stored key -> research/data/gate_account/*.json (gitignored, personal data)."""
import json, time, urllib.error
from pathlib import Path
import gate_auth as g
OUT = Path(__file__).parent / "data" / "gate_account"; OUT.mkdir(parents=True, exist_ok=True)
now = int(time.time()); d30 = f"from={now-29*86400}&to={now}"
EP = {  # name: (path, query)
 "total_balance": ("/wallet/total_balance", ""), "spot_accounts": ("/spot/accounts", ""), "spot_open_orders": ("/spot/open_orders", ""),
 "spot_account_book": ("/spot/account_book", "limit=500"), "spot_my_trades": ("/spot/my_trades", "limit=1000"),
 "spot_my_trades_30d": ("/spot/my_trades", f"limit=1000&{d30}"), "deposits": ("/wallet/deposits", "limit=500"), "withdrawals": ("/wallet/withdrawals", "limit=500"),
 "small_balance": ("/wallet/small_balance", ""), "small_balance_history": ("/wallet/small_balance_history", "limit=100"), "sub_account_balances": ("/wallet/sub_account_balances", ""),
 "saved_address": ("/wallet/saved_address", "currency=USDT"), "flash_swap_orders": ("/flash_swap/orders", "limit=100"), "margin_accounts": ("/margin/accounts", ""),
 "earn_uni_lends": ("/earn/uni/lends", ""), "earn_uni_interests": ("/earn/uni/interests/USDT", ""), "earn_dual_orders": ("/earn/dual/orders", ""), "earn_staking": ("/earn/staking/order_list", ""),
 "alpha_accounts": ("/alpha/accounts", ""), "alpha_orders": ("/alpha/orders", "limit=100"), "alpha_account_book": ("/alpha/account_book", "limit=100"),
 "futures_usdt_account": ("/futures/usdt/accounts", ""), "futures_usdt_positions": ("/futures/usdt/positions", ""), "futures_usdt_trades": ("/futures/usdt/my_trades", "limit=100"),
 "futures_usdt_book": ("/futures/usdt/account_book", f"limit=100&{d30}"), "futures_btc_account": ("/futures/btc/accounts", ""), "delivery_account": ("/delivery/usdt/accounts", ""),
 "options_account": ("/options/accounts", ""), "unified_accounts": ("/unified/accounts", ""), "account_detail": ("/account/detail", ""), "main_keys": ("/account/main_keys", ""),
 "fee": ("/wallet/fee", ""), "trade_fee_cent": ("/wallet/fee", "currency_pair=CENT_USDT"), "rewards": ("/rewards/getUserRewardsList", ""), "tradfi_account": ("/tradfi/users/assets", ""),
}
if __name__ == "__main__":
    for name, (path, q) in EP.items():
        try:
            r = g.call("GET", path, q); (OUT / f"{name}.json").write_text(json.dumps(r, indent=1))
            n = len(r) if isinstance(r, list) else "obj"; print(f"OK   {name:24s} {n}")
        except urllib.error.HTTPError as e:
            print(f"{e.code}  {name:24s} {e.read().decode()[:110]}")
        except Exception as e: print(f"ERR  {name:24s} {e}")
        time.sleep(0.15)

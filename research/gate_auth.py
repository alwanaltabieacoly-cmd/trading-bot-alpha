"""Gate.io signed client. Two environments, two credential entries in Windows Credential Manager:
  live    service 'alpha-gate'          https://api.gateio.ws            READ-ONLY unless ALPHA_GATE_TRADE=1
  testnet service 'alpha-gate-testnet'  https://api-testnet.gateapi.io   fake money, futures only, orders allowed
Commands:  set [live|testnet]   check [env]   audit   (audit inspects the live key)
"""
import hashlib, hmac, json, os, subprocess, sys, time, urllib.request

ENVS = {"live": ("alpha-gate", "https://api.gateio.ws"), "testnet": ("alpha-gate-testnet", "https://api-testnet.gateapi.io")}
DANGEROUS = {"withdraw", "wallet", "p2p", "account", "sub_accounts", "custody", "otc", "pay", "loan", "quant", "copy"}

def creds(env="live"):
    service = ENVS[env][0]
    import keyring  # lazy: the GitHub runner has no Windows Credential Manager, and the unit tests never need keys
    k, s = keyring.get_password(service, "key"), keyring.get_password(service, "secret")
    if not (k and s): raise SystemExit(f"No {env} key stored. Run: python research/gate_auth.py set {env}")
    return k, s

def call(method, path, query="", body="", env="live"):
    if method != "GET" and env == "live" and os.environ.get("ALPHA_GATE_TRADE") != "1":
        raise SystemExit(f"Blocked {method} {path}: live is read-only. Orders need ALPHA_GATE_TRADE=1 and a passed trade gate.")
    k, s = creds(env); ts = str(int(time.time()))
    sig = hmac.new(s.encode(), f"{method}\n/api/v4{path}\n{query}\n{hashlib.sha512(body.encode()).hexdigest()}\n{ts}".encode(), hashlib.sha512).hexdigest()
    req = urllib.request.Request(f"{ENVS[env][1]}/api/v4{path}" + (f"?{query}" if query else ""), data=body.encode() or None, method=method,
                                 headers={"KEY": k, "Timestamp": ts, "SIGN": sig, "Accept": "application/json", "Content-Type": "application/json", "User-Agent": "alpha"})
    return json.load(urllib.request.urlopen(req, timeout=20))

def _clipboard(label):
    input(f"Copy the Gate API {label} (Ctrl+C on Gate's page), then press Enter here: ")
    v = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True).stdout.strip()
    if len(v) < 16: raise SystemExit(f"Clipboard holds {len(v)} chars, too short for a {label}. Nothing stored.")
    print(f"  read {len(v)} chars"); return v

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"; env = sys.argv[2] if len(sys.argv) > 2 else "live"
    if cmd == "set":
        key = _clipboard("key"); secret = _clipboard("secret")
        import keyring
        keyring.set_password(ENVS[env][0], "key", key); keyring.set_password(ENVS[env][0], "secret", secret)
        subprocess.run(["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value ' '"])
        print(f"stored {env} key in Windows Credential Manager (service '{ENVS[env][0]}'); clipboard cleared")
    elif cmd == "audit":
        k, _ = creds("live"); me = next(x for x in call("GET", "/account/main_keys") if x.get("key") == k)
        bad = sorted(p["name"] for p in me["perms"] if not p["read_only"] and p["name"] in DANGEROUS)
        print("dangerous writable permissions:", bad or "none"); print("ip whitelist:", me.get("ip_whitelist") or "NONE")
        sys.exit(1 if bad or not me.get("ip_whitelist") else 0)
    elif cmd == "check" and env == "live":
        fee = call("GET", "/wallet/fee", "currency_pair=BTC_USDT")
        print("spot fees BTC_USDT: taker", fee.get("taker_fee"), "maker", fee.get("maker_fee"))
        print("key permissions:", json.dumps(call("GET", "/account/detail").get("key", {})))
    elif cmd == "check":
        a = call("GET", "/futures/usdt/accounts", env="testnet")
        print("testnet futures account:", {k: a.get(k) for k in ("total", "available", "currency")})

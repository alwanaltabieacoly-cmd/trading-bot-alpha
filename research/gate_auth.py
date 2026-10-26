"""Gate.io API key store in Windows Credential Manager (never in files or chat).
Set once:   python research/gate_auth.py set      (prompts, hidden input)
Check:      python research/gate_auth.py check    (read-only call: shows fee rates + key permissions)
"""
import getpass, hashlib, hmac, json, sys, time, urllib.request
import keyring

SERVICE, HOST = "alpha-gate", "https://api.gateio.ws"

def creds():
    k, s = keyring.get_password(SERVICE, "key"), keyring.get_password(SERVICE, "secret")
    if not (k and s): raise SystemExit("No Gate key stored. Run: python research/gate_auth.py set")
    return k, s

def call(method, path, query="", body=""):
    k, s = creds(); ts = str(int(time.time()))
    sig = hmac.new(s.encode(), f"{method}\n/api/v4{path}\n{query}\n{hashlib.sha512(body.encode()).hexdigest()}\n{ts}".encode(), hashlib.sha512).hexdigest()
    req = urllib.request.Request(f"{HOST}/api/v4{path}" + (f"?{query}" if query else ""), data=body.encode() or None, method=method,
                                 headers={"KEY": k, "Timestamp": ts, "SIGN": sig, "Accept": "application/json", "Content-Type": "application/json", "User-Agent": "alpha"})
    return json.load(urllib.request.urlopen(req, timeout=20))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "set":
        keyring.set_password(SERVICE, "key", getpass.getpass("Gate API key: ").strip())
        keyring.set_password(SERVICE, "secret", getpass.getpass("Gate API secret: ").strip())
        print("stored in Windows Credential Manager (service 'alpha-gate')")
    elif cmd == "check":
        fee = call("GET", "/wallet/fee", "currency_pair=BTC_USDT")
        print("spot fees BTC_USDT: taker", fee.get("taker_fee"), "maker", fee.get("maker_fee"))
        print("key permissions:", json.dumps(call("GET", "/account/detail").get("key", {})))

"""Gate.io API key store in Windows Credential Manager (never in files or chat).
Set once:   python research/gate_auth.py set      (prompts, hidden input)
Check:      python research/gate_auth.py check    (read-only call: shows fee rates + key permissions)
"""
import hashlib, hmac, json, subprocess, sys, time, urllib.request
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
        def from_clipboard(label):
            input(f"Copy the Gate API {label} (Ctrl+C on Gate's page), then press Enter here: ")
            v = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True).stdout.strip()
            if len(v) < 16: raise SystemExit(f"Clipboard holds {len(v)} chars, too short for a {label}. Nothing stored.")
            print(f"  read {len(v)} chars")
            return v
        key = from_clipboard("key"); secret = from_clipboard("secret")
        keyring.set_password(SERVICE, "key", key); keyring.set_password(SERVICE, "secret", secret)
        subprocess.run(["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value ' '"])
        print("stored in Windows Credential Manager (service 'alpha-gate'); clipboard cleared")
    elif cmd == "check":
        fee = call("GET", "/wallet/fee", "currency_pair=BTC_USDT")
        print("spot fees BTC_USDT: taker", fee.get("taker_fee"), "maker", fee.get("maker_fee"))
        print("key permissions:", json.dumps(call("GET", "/account/detail").get("key", {})))

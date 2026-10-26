"""Telegram notifications for the Gate bot. Token and chat id come from env TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID (GitHub Actions secrets)
or Windows Credential Manager service 'alpha-telegram'. With neither, send() prints and returns False, so nothing breaks.
  python research/gate_notify.py set        store the token (from clipboard) and find your chat id (send your bot any message first)
  python research/gate_notify.py test       send a test message
  python research/gate_notify.py say TEXT   send TEXT (used by workflows)"""
import json, os, subprocess, sys, urllib.parse, urllib.request
SERVICE = "alpha-telegram"

def creds():
    t, c = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if t and c: return t, c
    try:
        import keyring
        return keyring.get_password(SERVICE, "token"), keyring.get_password(SERVICE, "chat_id")
    except Exception: return None, None

def send(text):
    token, chat = creds()
    if not (token and chat): print("telegram not configured, message not sent"); return False
    data = urllib.parse.urlencode({"chat_id": chat, "text": text[:4000], "disable_web_page_preview": "true"}).encode()
    try: r = json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data, timeout=15))
    except Exception as e: print(f"telegram failed: {type(e).__name__}"); return False   # never print the URL or the error text: they contain the token
    print(f"telegram sent (message_id {r['result']['message_id']})" if r.get("ok") else "telegram refused the message"); return bool(r.get("ok"))

def _chat_id(token):
    for u in reversed(json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15))["result"]):
        m = u.get("message") or u.get("my_chat_member") or {}
        if m.get("chat", {}).get("type") == "private": return str(m["chat"]["id"])
    raise SystemExit("no message found: open your bot in Telegram, press Start, send 'hi', then run again")

if __name__ == "__main__":
    if sys.argv[1:2] == ["set"]:
        input("Copy the bot token from BotFather, then press Enter: ")
        token = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True).stdout.strip()
        if ":" not in token or len(token) < 30: raise SystemExit("clipboard does not look like a bot token; nothing stored")
        chat = _chat_id(token); import keyring
        keyring.set_password(SERVICE, "token", token); keyring.set_password(SERVICE, "chat_id", chat)
        subprocess.run(["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value ' '"]); print("stored; clipboard cleared")
    elif sys.argv[1:2] == ["test"]: print("sent" if send("Alpha: Telegram link works.") else "not sent")
    elif sys.argv[1:2] == ["say"]: sys.exit(0 if send(" ".join(sys.argv[2:])) else 1)
    else: print(__doc__)

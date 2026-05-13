# 텔레그램 알림 발송.

import httpx
from ..keys.api_keys import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, get_key


def send(text: str, parse_mode: str = "Markdown") -> dict:
    token = get_key("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    chat_id = get_key("TELEGRAM_CHAT_ID") or TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return {"ok": False, "error": "텔레그램 BOT_TOKEN / CHAT_ID 미설정"}
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        r = httpx.post(url, json=body, timeout=10.0)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:120]}"}
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

"""
Telegram integration for CogniShift.

- send_message(chat_id, text) — sends a message via Bot API
- format_notification(...)    — builds the message shown to the user
- get_deep_link(user_id)      — returns the ?start= link for account linking
"""
import json
import requests
from django.conf import settings

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _api(method: str, payload: dict) -> dict:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return {}
    url = TELEGRAM_API.format(token=token, method=method)
    try:
        # Serialize manually with ensure_ascii=False so emojis survive on Windows
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        resp = requests.post(
            url,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=5,
        )
        return resp.json()
    except Exception as e:
        print(f"[Telegram] {method} failed: {e}".encode("utf-8").decode("utf-8", errors="replace"))
        return {}


def send_message(chat_id: str, text: str) -> bool:
    """Send a plain-text message to a chat. Returns True on success."""
    result = _api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    })
    ok = result.get("ok", False)
    if not ok:
        desc = result.get("description", "unknown error")
        print(f"[Telegram] sendMessage failed: {desc}")
    return ok


def format_notification(
    source_app: str,
    message: str,
    priority: str,
    category: str,
    decision: str,
    inferred_mode: str,
) -> str:
    """Build the Telegram message shown to the user for a notification."""
    PRIORITY_LABEL = {"high": "\U0001f534 high", "medium": "\U0001f7e1 medium", "low": "\U0001f7e2 low"}.get(priority, priority)
    DECISION_LABEL = {"send": "\u2705 Delivered", "delay": "\u23f3 Delayed", "block": "\U0001f6ab Blocked"}.get(decision, decision)
    SOURCE_LABEL = {
        "slack": "\U0001f4ac Slack",
        "gmail": "\U0001f4e7 Gmail",
        "github": "\U0001f419 GitHub",
        "calendar": "\U0001f4c5 Calendar",
        "youtube": "\u25b6\ufe0f YouTube",
    }.get(source_app, source_app.capitalize())

    return (
        f"\U0001f514 <b>CogniShift</b> \u2014 {DECISION_LABEL}\n\n"
        f"<b>Source:</b> {SOURCE_LABEL}\n"
        f"<b>Message:</b> {message}\n\n"
        f"<b>Priority:</b> {PRIORITY_LABEL}\n"
        f"<b>Category:</b> {category}\n"
        f"<b>Mode detected:</b> {inferred_mode}"
    )


def get_deep_link(user_id: str) -> str:
    """Returns the t.me link the user clicks to connect their Telegram account."""
    username = settings.TELEGRAM_BOT_USERNAME
    payload = str(user_id).replace("-", "_")
    return f"https://t.me/{username}?start={payload}"

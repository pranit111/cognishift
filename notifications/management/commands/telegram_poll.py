"""
python manage.py telegram_poll

Long-polls the Telegram Bot API for updates.
Handles /start <user_id_payload> to link a user's Telegram account.

Run this in a separate terminal alongside the Django dev server.
"""
import time

import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from notifications.models import User
from notifications.telegram import send_message


TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _get(method: str, params: dict = None) -> dict:
    url = TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)
    try:
        resp = requests.get(url, params=params or {}, timeout=35)
        return resp.json()
    except Exception as e:
        print(f"[Poll] Request failed: {e}")
        return {}


def _handle_update(update: dict):
    message = update.get("message") or update.get("channel_post")
    if not message:
        return

    chat_id = str(message["chat"]["id"])
    text = message.get("text", "").strip()

    if not text.startswith("/start"):
        return

    # /start <payload>  where payload is user UUID with hyphens replaced by underscores
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        send_message(chat_id, "👋 Hi! Use your CogniShift profile link to connect your account.")
        return

    payload = parts[1].strip()
    user_id_str = payload.replace("_", "-")  # restore UUID hyphens

    try:
        user = User.objects.get(id=user_id_str)
    except (User.DoesNotExist, Exception):
        send_message(chat_id, "❌ Invalid link. Please generate a new one from your CogniShift profile.")
        return

    # Save chat_id
    user.telegram_chat_id = chat_id
    user.save(update_fields=["telegram_chat_id"])

    send_message(
        chat_id,
        f"✅ <b>Connected!</b>\n\n"
        f"Hey <b>{user.name}</b>, your CogniShift notifications will now appear here.\n\n"
        f"Role: {user.role} | Pref: {user.notification_pref}",
    )
    print(f"[Poll] Linked user {user.name} ({user.id}) → chat_id {chat_id}")


class Command(BaseCommand):
    help = "Long-poll Telegram Bot API and handle /start commands for account linking."

    def handle(self, *args, **kwargs):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stderr.write("TELEGRAM_BOT_TOKEN is not set in .env")
            return

        self.stdout.write(self.style.SUCCESS(
            "Telegram polling started. Press Ctrl+C to stop."
        ))

        offset = None
        while True:
            params = {"timeout": 30, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset

            data = _get("getUpdates", params)

            if not data.get("ok"):
                self.stderr.write(f"getUpdates error: {data}")
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    _handle_update(update)
                except Exception as e:
                    self.stderr.write(f"Error handling update: {e}")

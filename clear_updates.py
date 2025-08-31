"""
Utility to clear pending Telegram getUpdates backlog for the configured bot.

Usage:
    python clear_updates.py

What it does:
- Calls getUpdates to inspect queued updates.
- If any are present, calls getUpdates again with offset=last_update_id+1 to mark them as handled.

This avoids your long-polling listener immediately seeing old messages when it starts.
"""

import requests
from config import TELEGRAM_BOT_TOKEN

API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def get_updates():
    url = f"{API}/getUpdates"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("result", [])


def clear_backlog():
    updates = get_updates()
    if not updates:
        print("No pending updates to clear.")
        return

    last_id = updates[-1]["update_id"]
    print(f"Found {len(updates)} updates. Clearing up to update_id {last_id}...")
    url = f"{API}/getUpdates"
    params = {"offset": last_id + 1}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    print("Cleared updates.")


if __name__ == "__main__":
    try:
        clear_backlog()
    except Exception as e:
        print(f"Error while clearing updates: {e}")

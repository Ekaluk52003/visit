#!/usr/bin/env python3
"""
Helper script to get your Telegram Chat ID
Run this after sending a message to your bot
"""

import requests
import json

# Your bot token (already configured)
BOT_TOKEN = "8061689089:AAHWzPbQP-Re6cS24yqNDEsSvy-gubj9Idg"

def get_chat_id():
    """Get the chat ID from recent messages to your bot"""

    print("🔍 Looking for your Chat ID...")
    print("=" * 50)
    print("Make sure you've sent at least one message to your bot first!")
    print()

    try:
        # Get updates from Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return

        data = response.json()

        if not data.get('ok'):
            print(f"❌ Telegram API error: {data.get('description', 'Unknown error')}")
            return

        updates = data.get('result', [])

        if not updates:
            print("❌ No messages found!")
            print("\n📝 Steps to fix this:")
            print("1. Open Telegram")
            print("2. Find your bot")
            print("3. Send any message to it (like 'Hello')")
            print("4. Run this script again")
            return

        # Get the most recent message
        latest_update = updates[-1]

        if 'message' in latest_update:
            chat_id = latest_update['message']['chat']['id']
            chat_type = latest_update['message']['chat']['type']

            if 'first_name' in latest_update['message']['chat']:
                name = latest_update['message']['chat']['first_name']
            else:
                name = latest_update['message']['chat'].get('title', 'Unknown')

            print("✅ Found your Chat ID!")
            print(f"📱 Chat ID: {chat_id}")
            print(f"👤 Name: {name}")
            print(f"🔗 Type: {chat_type}")
            print()
            print("📋 Copy this Chat ID to your config.py:")
            print(f'TELEGRAM_CHAT_ID = "{chat_id}"')
            print()

            # Show how to update config.py
            print("🔧 Or run this command to update config.py automatically:")
            print(f"python -c \"")
            print(f"with open('config.py', 'r') as f: content = f.read(); ")
            print(f"content = content.replace('YOUR_CHAT_ID_HERE', '{chat_id}'); ")
            print(f"with open('config.py', 'w') as f: f.write(content)\"")

        else:
            print("❌ No message found in the latest update")
            print("Full response:")
            print(json.dumps(data, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("Please check your internet connection and try again.")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    get_chat_id()

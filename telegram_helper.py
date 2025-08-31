import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

def send_telegram_message(message):
    """
    Send a message to Telegram bot

    Args:
        message (str): The message to send

    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"  # Allows basic HTML formatting
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("✅ Message sent to Telegram successfully")
            return True
        else:
            print(f"❌ Failed to send message to Telegram: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error sending message to Telegram: {str(e)}")
        return False

def send_dialog_alert(dialog_type, dialog_message, timestamp=None):
    """
    Send a formatted dialog alert to Telegram

    Args:
        dialog_type (str): Type of dialog (alert, confirm, etc.)
        dialog_message (str): The dialog message
        timestamp (datetime, optional): When the dialog occurred
    """
    if timestamp is None:
        timestamp = datetime.now()

    formatted_message = f"""
🚨 <b>VisitBRP Dialog Alert</b>

<b>Type:</b> {dialog_type}
<b>Time:</b> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
<b>Message:</b> {dialog_message}

<i>Automation is handling this dialog...</i>
    """.strip()

    return send_telegram_message(formatted_message)

def send_automation_status(status, details="", round_choice=None):
    """
    Send automation status updates to Telegram

    Args:
        status (str): Status message (e.g., "Started", "Completed", "Error")
        details (str): Additional details
    """
    timestamp = datetime.now()

    status_emoji = {
        "started": "🚀",
        "completed": "✅",
        "error": "❌",
        "warning": "⚠️"
    }

    emoji = status_emoji.get(status.lower(), "ℹ️")

    message = f"""
{emoji} <b>VisitBRP Automation</b>

<b>Status:</b> {status}
<b>Time:</b> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""

    if round_choice is not None:
        message += f"<b>Round:</b> {round_choice}\n"

    if details:
        message += f"<b>Details:</b> {details}\n"

    return send_telegram_message(message.strip())

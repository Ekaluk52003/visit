(# VisitBRP Playwright Automation with Telegram Integration

This repository contains a Playwright-based Python automation that navigates the VisitBRP booking flow and exercises the UI to select a prisoner, fill ID fields, and submit the form. It now includes **Telegram bot integration** to send real-time notifications about dialog messages and automation status.

## What this project does

- Navigates to the VisitBRP page used for visitor booking.
- Selects the first prisoner checkbox.
- Fills visitor ID fields and submits the booking flow.
- Interacts with search/add dialogs and selects a visit round (calculated as tomorrow's day).
- Captures screenshots at important steps and prints dialog messages to the console.
- **NEW**: Sends real-time notifications to your Telegram bot when dialogs appear or automation status changes.

## Files of interest

- `main.py` — the Playwright script (single-file automation) with Telegram integration.
- `telegram_helper.py` — Telegram bot helper functions for sending notifications.
- `config.py` — Configuration file for Telegram bot credentials.
- `test_telegram.py` — Test script to verify Telegram bot functionality.
- `after_first_submit.png`, `alert_screenshot.png`, `after_final_click.png` — screenshots produced by the script when running.

## Prerequisites

- Windows with PowerShell (instructions below use your default `pwsh`).
- Python 3.11 (or similar supported by Playwright/uv).
- `uv` (the project tool used in this workspace) — used here to manage the virtual env and dependencies.
- **Telegram bot token and chat ID** (see setup instructions below).

## Setup Instructions

### 1. Prepare the Python Environment

If you haven't already prepared the project, run these commands from the project root (`d:\python\visit`) in PowerShell:

```powershell
# initialize project (if not yet initialized)
uv init

# add dependencies to the project and create a .venv
uv add playwright requests

# install Playwright browsers
uv run playwright install
```

### 2. Set Up Telegram Bot (NEW)

#### Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Send `/newbot`** command to BotFather
3. **Follow the prompts** to choose a name and username for your bot
4. **Save the bot token** that BotFather provides (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Get Your Chat ID

1. **Send a message** to your newly created bot (any message)
2. **Visit this URL** in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. **Find your chat ID** in the JSON response (look for `"chat":{"id":YOUR_CHAT_ID}`)

#### Configure the Bot

1. **Edit `config.py`** and replace the placeholder values:
   ```python
   TELEGRAM_BOT_TOKEN = ""  # Your actual bot token
   TELEGRAM_CHAT_ID = ""  # Your actual chat ID
   ```

#### Test Your Configuration

Run the test script to verify everything is working:

```powershell
uv run python test_telegram.py
```

You should receive test messages in your Telegram chat. If the test fails, double-check your bot token and chat ID.

## Run the automation

From the repository root run:

```powershell
uv run python main.py
```

This launches Chromium (by default in non-headless mode) and walks through the booking steps. The script:
- Sends a "Started" notification to Telegram when automation begins
- Sends dialog alerts to Telegram whenever browser dialogs appear
- Sends a "Completed" notification when automation finishes successfully
- Sends error notifications if anything goes wrong

## Telegram Features

The integration provides three types of notifications:

### 1. Dialog Alerts 🚨
Sent whenever the automation encounters a browser dialog (alert, confirm, etc.):
- Dialog type and message
- Timestamp
- Automatic handling notification

### 2. Status Updates 🚀
Sent at key automation milestones:
- ✅ Started: When automation begins
- ✅ Completed: When automation finishes successfully
- ❌ Error: If automation encounters an error

### 3. Custom Messages 💬
You can send custom messages using the helper functions in your code.


## Security Best Practices

### Using Environment Variables (Recommended)

Instead of hardcoding credentials in `config.py`, you can use environment variables:

1. **Set environment variables** in PowerShell:
   ```powershell
   $env:TELEGRAM_BOT_TOKEN = "your_bot_token_here"
   $env:TELEGRAM_CHAT_ID = "your_chat_id_here"
   ```

2. **Update `config.py`**:
   ```python
   import os
   TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "fallback_token")
   TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "fallback_chat_id")
   ```

### .gitignore

Make sure to add `config.py` to your `.gitignore` file if you're using version control:
```
config.py
*.png
.venv/
```

## How the script handles alerts and dialogs

The script registers a `dialog` handler that prints the dialog type and message to the console, waits briefly so the alert is visible, and then accepts it. If you need the alert screenshot, look for `alert_screenshot.png` in the project root.

If you aren't seeing the dialog in the browser UI while the script runs, try the following:

- Run the script non-headless (default in `main.py`) and watch the browser window.
- Increase the `time.sleep` value in the dialog handler to keep the alert visible longer.
- Remove screenshot capture from the handler if Playwright errors occur when taking screenshots inside the dialog callback (some environments may throw in that callback); instead, take a screenshot after the click and before the dialog auto-closes.

## Troubleshooting common issues

- Timeout when finding elements: increase waits or use `page.wait_for_selector(selector, timeout=...)` before interacting.
- Clicks are intercepted by labels or other elements: prefer `page.check('#id')` for checkboxes or click the associated `label[for=...]`.
- Dialogs not captured: ensure script runs in the same page context and the `page.on('dialog', ...)` handler is registered before the action that triggers the alert.
- Screenshot not created: check file permissions and script exceptions in the console.

## Development notes and next steps

- Consider extracting selectors and test data into a small config at the top of `main.py` for easier maintenance.
- Add unit tests or a small smoke test to validate the happy path.
- If you need more robust interaction with the page (for example AJAX waits), replace static sleeps with `page.wait_for_function(...)` checks.

## Contact / Follow up

If you want, I can:
- Make the script idempotent and add retries for flaky steps.
- Add explicit error logging and a small test harness.
- Convert this single script into a small test suite with Playwright test runner.

---

Generated on: Aug 31, 2025
```

## Webhook (ngrok) setup

If you prefer Telegram webhooks over long-polling, you can expose the local `telegram_webhook.py` server using ngrok and tell Telegram to send updates to the public HTTPS URL.

1. Download or install ngrok (https://ngrok.com/) and sign in to get your auth token.

2. Start the webhook server locally (default port 8000):

```powershell
# from project root
python telegram_webhook.py
```

3. In a separate terminal, start ngrok to forward HTTPS to the webhook port:

```powershell
ngrok http 8000
```

4. In the ngrok output you'll see a forwarding HTTPS URL like `https://abcd-1234.ngrok.io`.

5. Set the Telegram webhook for your bot (replace <YOUR_BOT_TOKEN> and <NGROK_HOST>):

```powershell
# example using curl (PowerShell)
$ngrokUrl = "https://abcd-1234.ngrok.io"  # replace with your ngrok https URL
$botToken = "<YOUR_BOT_TOKEN>"
$webhookUrl = "$ngrokUrl/webhook"
curl -X POST "https://api.telegram.org/bot$botToken/setWebhook" -F "url=$webhookUrl"
```

6. (Optional) If you enabled `TELEGRAM_WEBHOOK_SECRET` in `config.py` or set it as an environment variable, add the secret when setting the webhook so Telegram includes it in the `X-Telegram-Bot-Api-Secret-Token` header:

```powershell
$secret = "mysecretvalue"
curl -X POST "https://api.telegram.org/bot$botToken/setWebhook" -F "url=$webhookUrl" -F "secret_token=$secret"
```

7. Test by sending a message to your bot. The webhook server will receive the update and handle commands as described above.

To remove the webhook and revert to getUpdates/polling, use:

```powershell
curl "https://api.telegram.org/bot$botToken/deleteWebhook"
```

Security note: webhook URLs must be HTTPS. Use ngrok (or a hosted HTTPS endpoint). Keep your bot token and optional secret private.

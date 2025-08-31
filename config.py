# Telegram Bot Configuration
# Prefer loading secrets from a .env file or environment variables.
import os
from pathlib import Path

# If a .env file is present, prefer python-dotenv (if installed); otherwise parse it manually.
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv

        # Ensure .env values override any pre-set environment variables
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    except Exception:
        # Fallback: parse simple KEY=VALUE lines and OVERRIDE environment variables.
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if not ln or ln.startswith("#"):
                        continue
                    if "=" in ln:
                        k, v = ln.split("=", 1)
                        v = v.strip().strip('"').strip("'")
                        os.environ[k.strip()] = v
        except Exception:
            pass

# Values are read from environment variables. For production, do NOT keep hardcoded secrets here.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Support either a single chat id or multiple comma-separated chat ids.
_single_chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
_multi_chat_ids = (os.getenv("TELEGRAM_CHAT_IDS") or "").strip()

if _multi_chat_ids:
    TELEGRAM_CHAT_IDS = [s.strip()
                         for s in _multi_chat_ids.split(",") if s.strip()]
elif _single_chat_id:
    TELEGRAM_CHAT_IDS = [_single_chat_id]
else:
    TELEGRAM_CHAT_IDS = []  # empty means "allow any chat" if the app chooses to

# Backward-compat single value (first of the list, or empty string)
TELEGRAM_CHAT_ID = TELEGRAM_CHAT_IDS[0] if TELEGRAM_CHAT_IDS else ""

# Fail fast only for the required token; chat id(s) can be optional depending on app policy.
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "Missing required environment variable: TELEGRAM_BOT_TOKEN")

# End of config

# Telegram Bot Configuration
# Prefer loading secrets from a .env file or environment variables.
import os
from pathlib import Path

# If a .env file is present, prefer python-dotenv (if installed); otherwise parse it manually.
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
	try:
		from dotenv import load_dotenv

		load_dotenv(dotenv_path=ENV_PATH)
	except Exception:
		# Fallback: parse simple KEY=VALUE lines and set environment variables if missing.
		try:
			with open(ENV_PATH, "r", encoding="utf-8") as fh:
				for ln in fh:
					ln = ln.strip()
					if not ln or ln.startswith("#"):
						continue
					if "=" in ln:
						k, v = ln.split("=", 1)
						v = v.strip().strip('"').strip("'")
						os.environ.setdefault(k.strip(), v)
		except Exception:
			pass

# Values are read from environment variables. For production, do NOT keep hardcoded secrets here.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Fail fast if required configuration is missing.
missing = []
if not TELEGRAM_BOT_TOKEN:
	missing.append("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_CHAT_ID:
	missing.append("TELEGRAM_CHAT_ID")
if missing:
	raise RuntimeError(
		"Missing required environment variables: "
		+ ", ".join(missing)
	)

# End of config

"""
Simple Telegram listener that starts the automation when a Telegram message is received.

Usage:
    uv run python telegram_listener.py

Behavior:
- Long-polls Telegram getUpdates for new messages.
- When a message is received from the configured chat ID (or any if TELEGRAM_CHAT_ID is empty),
  it sends an acknowledgement and starts `main.py` in a separate Python subprocess.
- Prevents multiple concurrent automation runs.

Notes:
- Configure your bot token and chat id in `config.py` as before.
- This file uses the same `TELEGRAM_BOT_TOKEN` and optional `TELEGRAM_CHAT_ID` from `config.py`.
"""

import time
import sys
import subprocess
import requests
import os
from typing import Optional

try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except Exception as e:
    # Config may raise a RuntimeError when required env vars are missing.
    print("Configuration error while loading `config.py`:", str(e))
    print("Make sure you have a .env file or environment variables set for TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
    print("Example .env:\nTELEGRAM_BOT_TOKEN=your_token_here\nTELEGRAM_CHAT_ID=your_chat_id_here")
    import sys

    sys.exit(1)

from telegram_helper import send_telegram_message
import json
import threading
from datetime import datetime, time as dt_time, date as dt_date

GET_UPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
PENDING_RUNS_FILE = os.path.join(os.path.dirname(__file__), "pending_runs.json")
# Default schedule time when queued jobs should be launched (09:30 local server time)
SCHEDULE_HOUR = 16
SCHEDULE_MINUTE = 16
SCHEDULER_WAKE_SEC = 30  # how often scheduler checks the queue

# Shared process handle for the currently running automation (module scope)
current_proc = None


def fetch_updates(offset: Optional[int] = None, timeout: int = 20):
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    try:
        resp = requests.get(GET_UPDATES_URL, params=params, timeout=timeout + 10)
        resp.raise_for_status()
        return resp.json().get("result", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates: {e}")
        return []


def start_automation_subprocess(round_arg=None):
    """Start main.py in a separate Python subprocess and return the Popen object.
    If round_arg is provided it will be passed as a positional argument to main.py.
    """
    python_exe = sys.executable or "python"
    cmd = [python_exe, "main.py"]
    if round_arg:
        cmd.append(str(round_arg))
    print(f"Starting automation using: {' '.join(cmd)}")
    # Use Popen so we don't block the listener; inherit stdout/stderr
    proc = subprocess.Popen(cmd, cwd=".")
    return proc


def load_pending_runs():
    if not os.path.exists(PENDING_RUNS_FILE):
        return []
    try:
        with open(PENDING_RUNS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []


def save_pending_runs(runs):
    try:
        with open(PENDING_RUNS_FILE, "w", encoding="utf-8") as fh:
            json.dump(runs, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save pending runs: {e}")


def schedule_run(chat_id, round_choice):
    """Add a pending run scheduled for today's 09:30."""
    now = datetime.now()
    # scheduled_for kept as ISO date string for simplicity
    sched_date = now.date().isoformat()
    pending = load_pending_runs()
    pending.append({
        "chat_id": str(chat_id),
        "round": str(round_choice) if round_choice is not None else None,
        "requested_at": now.isoformat(),
        "scheduled_for": sched_date,
    })
    save_pending_runs(pending)


def process_pending_runs_loop():
    while True:
        try:
            now = datetime.now()
            today_str = now.date().isoformat()
            target_dt = datetime.combine(now.date(), dt_time(SCHEDULE_HOUR, SCHEDULE_MINUTE))
            if now >= target_dt:
                pending = load_pending_runs()
                remaining = []
                for job in pending:
                    if job.get("scheduled_for") == today_str:
                        # attempt to launch (respect current_proc concurrency)
                        proc = globals().get('current_proc')
                        try:
                            running = proc is not None and proc.poll() is None
                        except Exception:
                            running = False

                        if running:
                            # automation running, keep job for later
                            remaining.append(job)
                            continue

                        round_choice = job.get("round")
                        try:
                            print(f"Launching scheduled run (round={round_choice}) from pending queue")
                            new_proc = start_automation_subprocess(round_choice)
                            globals()['current_proc'] = new_proc
                            send_telegram_message(f"Scheduled automation launched (round={round_choice}).")
                        except Exception as e:
                            print(f"Failed to launch scheduled job: {e}")
                            # keep the job to try again later
                            remaining.append(job)
                    else:
                        remaining.append(job)
                save_pending_runs(remaining)
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(SCHEDULER_WAKE_SEC)


def main():
    print("Telegram listener starting...")
    # start background scheduler thread
    scheduler_thread = threading.Thread(target=process_pending_runs_loop, daemon=True)
    scheduler_thread.start()
    # On startup, fetch any pending updates and advance the offset so we don't
    # immediately process old messages that were sent before the listener started.
    last_update_id = None
    try:
        pending = fetch_updates(timeout=1)
        if pending:
            last_update_id = pending[-1].get("update_id")
            print(f"Found {len(pending)} pending update(s). Ignoring backlog up to update_id {last_update_id}.")
            print("If you want to process past messages instead, remove this startup-skip logic or run clear_updates.py first.")
    except Exception as e:
        print(f"Warning: failed to inspect pending updates on startup: {e}")
        last_update_id = None
    global current_proc
    current_proc = None

    while True:
        updates = fetch_updates(offset=(last_update_id + 1) if last_update_id is not None else None, timeout=30)

        for update in updates:
            last_update_id = update.get("update_id", last_update_id)

            message = update.get("message") or update.get("edited_message")
            if not message:
                continue

            chat = message.get("chat", {})
            chat_id = str(chat.get("id"))
            text = message.get("text", "")

            print(f"Received message from chat {chat_id}: {text}")

            # If TELEGRAM_CHAT_ID is set, only accept messages from that chat
            if TELEGRAM_CHAT_ID and str(TELEGRAM_CHAT_ID) != chat_id:
                print(f"Ignoring message from unknown chat {chat_id}")
                continue

            # Simple commands
            tokens = text.strip().split() if text else []
            cmd_word = tokens[0].lower() if tokens else None
            cmd_arg = tokens[1] if len(tokens) > 1 else None

            if cmd_word and cmd_word in ("/start", "start", "run"):
                # parse numeric arg if present
                chosen_round = cmd_arg if (cmd_arg and cmd_arg.isdigit()) else None

                # Decide whether to queue or run immediately based on schedule
                now = datetime.now()
                target_dt = datetime.combine(now.date(), dt_time(SCHEDULE_HOUR, SCHEDULE_MINUTE))

                if now < target_dt:
                    # queue for today's scheduled time
                    schedule_run(chat_id, chosen_round)
                    reply = f"Received. I will run this automation at {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} (round={chosen_round or 'default'})."
                    send_telegram_message(reply)
                else:
                    if current_proc is not None and current_proc.poll() is None:
                        reply = "Automation is already running."
                        print(reply)
                        send_telegram_message(reply)
                    else:
                        # Inform user which round value will be used
                        if chosen_round:
                            reply = f"Starting automation now (round={chosen_round})..."
                            current_proc = start_automation_subprocess(chosen_round)
                        else:
                            reply = "Starting automation now (round=default)..."
                            current_proc = start_automation_subprocess()
                        send_telegram_message(reply)
                        send_telegram_message("Automation launched (background process). I'll notify you when it finishes.")

            elif cmd_word and cmd_word in ("/pending", "pending"):
                pending = load_pending_runs()
                if not pending:
                    send_telegram_message("No pending scheduled runs.")
                else:
                    lines = ["Pending scheduled runs:"]
                    for i, job in enumerate(pending, start=1):
                        lines.append(f"{i}. scheduled_for={job.get('scheduled_for')} round={job.get('round') or 'default'} requested_at={job.get('requested_at')}")
                    send_telegram_message("\n".join(lines))

            elif cmd_word and cmd_word in ("/cancel", "cancel"):
                # cancel by 1-based index: /cancel 1
                if cmd_arg and cmd_arg.isdigit():
                    idx = int(cmd_arg) - 1
                    pending = load_pending_runs()
                    if 0 <= idx < len(pending):
                        job = pending.pop(idx)
                        save_pending_runs(pending)
                        send_telegram_message(f"Cancelled pending run {idx+1} (round={job.get('round') or 'default'}).")
                    else:
                        send_telegram_message(f"Invalid index. There are {len(pending)} pending jobs.")
                else:
                    send_telegram_message("Usage: /cancel N  (where N is the job number from /pending)")

            elif text and text.strip().lower() in ("/status", "status"):
                if current_proc is not None and current_proc.poll() is None:
                    send_telegram_message("Automation is currently running.")
                else:
                    send_telegram_message("No automation is running right now.")

            elif text and text.strip().lower() in ("/stop", "stop"):
                if current_proc is not None and current_proc.poll() is None:
                    current_proc.terminate()
                    send_telegram_message("Requested to stop the automation process.")
                else:
                    send_telegram_message("No running automation process to stop.")

            else:
                # Default behavior: any message triggers start (optional). We'll treat any non-command as start.
                if text:
                    if current_proc is not None and current_proc.poll() is None:
                        reply = "Automation is already running."
                        print(reply)
                        send_telegram_message(reply)
                    else:
                        reply = "Message received — starting automation now..."
                        send_telegram_message(reply)
                        try:
                            current_proc = start_automation_subprocess()
                            send_telegram_message("Automation launched (background process).")
                        except Exception as e:
                            err = f"Failed to start automation: {e}"
                            print(err)
                            send_telegram_message(err)

        # Short sleep to avoid tight loop in case of errors
        time.sleep(1)


if __name__ == "__main__":
    main()

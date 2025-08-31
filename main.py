from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
from telegram_helper import send_dialog_alert, send_automation_status
import sys
import os
from pathlib import Path

# Load runtime configuration from .env or environment variables.
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=ENV_PATH)
    except Exception:
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

# Values used by the automation (can be set via .env or environment):
VISIT_URL = os.getenv(
    "VISIT_URL"
)
ID_CARD1 = os.getenv("ID_CARD1")
ID_CARD2 = os.getenv("ID_CARD2")
MOBILE = os.getenv("MOBILE")

def main(round_choice=None):
    url = "http://visitbrp.com/%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%9A%E0%B8%88%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%A2%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A1%E0%B8%8D%E0%B8%B2%E0%B8%95%E0%B8%B4/"

    # Send automation start notification (include round if provided)
    details = "Beginning VisitBRP automation process"
    if round_choice:
        details += f" (round={round_choice})"
    send_automation_status("Started", details, round_choice=round_choice)

    try:
        headless = os.getenv("HEADLESS", "1") != "0"
        with sync_playwright() as p:
            browser = p.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",                # harmless for non-root, useful under some services
                "--disable-dev-shm-usage",     # avoids /dev/shm issues on small devices
            ],
        )
            page = browser.new_page()

            # Handle dialogs
            def handle_dialog(dialog):
                print(f"Dialog type: {dialog.type}")
                print(f"Dialog message: {dialog.message}")
                print("Alert visible for 15 seconds...")

                # Send dialog alert to Telegram
                send_dialog_alert(dialog.type, dialog.message)

                time.sleep(15)  # Wait 15 seconds to let the user see the dialog
                dialog.accept()  # or dialog.dismiss()

            page.on('dialog', handle_dialog)

            page.goto(url)

            # Wait for the page to load and locate the label for the checkbox
            page.wait_for_selector("label[for='cbxname1']")

            # Click the label to select the checkbox
            page.locator("label[for='cbxname1']").click()

            # Wait a moment for JavaScript to execute after checkbox selection
            page.wait_for_timeout(1000)

            # Wait for the submit button to be available
            page.wait_for_selector("input.submit")

            # Click the submit button
            page.locator("input.submit").click()

            # Wait for the input field to be available
            page.wait_for_selector("#idno")

            # Fill the input with the specified value
            page.fill("#idno", ID_CARD1)

            # Wait for the submit button to be available
            page.wait_for_selector("input.submit")

            # Click the submit button
            page.locator("input.submit").click()

                # Click the label to select the checkbox
            page.locator("label[for='cbxname1']").click()


             # Wait for the submit button to be available
            page.wait_for_selector("input.submit")

            # Click the submit button
            page.locator("input.submit").click()
            page.wait_for_selector("input.submit")

            # Wait for the search input field to be available
            page.wait_for_selector("#search_idno")

            # Fill the search input with the specified value
            page.fill("#search_idno", ID_CARD2)
            page.locator("input[value='เพิ่ม']").click()


            # Click the confirm button
            page.locator("input[value='ตกลง']").click()

            # Calculate the option value as tomorrow's day
            tomorrow = datetime.now() + timedelta(days=1)
            option_value = str(tomorrow.day)
            print(f"Option value: {option_value}")

            # Wait for the round select to be available
            page.wait_for_selector("#dd")

            # Select the option
            page.select_option("#dd", option_value)

            # Click outside the select to trigger any JavaScript
            page.locator("body").click()
            page.wait_for_selector("#round")
            # Use provided round_choice if given, otherwise fall back to '2'
            sel_round = str(round_choice) if round_choice else '2'
            page.select_option("#round", sel_round)

            page.fill("#mobile", MOBILE)
            page.locator("body").click()
                   # Click the confirm button
            page.locator("input[value='ตกลง']").click()

            # Optionally, keep the browser open for a moment to see the result
            page.wait_for_timeout(2000)  # Wait 2 seconds

            # Send completion notification
            send_automation_status("Completed", "VisitBRP automation finished successfully", round_choice=round_choice)

            browser.close()

    except Exception as e:
        error_message = f"Automation failed with error: {str(e)}"
        print(f"Error: {error_message}")
        send_automation_status("Error", error_message, round_choice=round_choice)
        raise

if __name__ == "__main__":
    # Optional positional argument: round value (e.g. python main.py 2)
    arg = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    main(arg)

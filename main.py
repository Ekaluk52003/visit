from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
from telegram_helper import send_dialog_alert, send_automation_status

def main():
    url = "http://visitbrp.com/%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%9A%E0%B8%88%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%A2%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A1%E0%B8%8D%E0%B8%B2%E0%B8%95%E0%B8%B4/"

    # Send automation start notification
    send_automation_status("Started", "Beginning VisitBRP automation process")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Set to True for headless mode
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
            page.fill("#idno", "4130300003031")

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
            page.fill("#search_idno", "4130300003023")
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
            page.select_option("#round", '2')

            page.fill("#mobile", "0991795649")
            page.locator("body").click()
                   # Click the confirm button
            page.locator("input[value='ตกลง']").click()

            # Optionally, keep the browser open for a moment to see the result
            page.wait_for_timeout(60000)  # Wait 60 seconds

            # Send completion notification
            send_automation_status("Completed", "VisitBRP automation finished successfully")

            browser.close()

    except Exception as e:
        error_message = f"Automation failed with error: {str(e)}"
        print(f"Error: {error_message}")
        send_automation_status("Error", error_message)
        raise

if __name__ == "__main__":
    main()

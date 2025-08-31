(# VisitBRP Playwright Automation

This repository contains a small Playwright-based Python automation that navigates the VisitBRP booking flow and exercises the UI to select a prisoner, fill ID fields, and submit the form. It was scaffolded using `uv` and Playwright.

## What this project does

- Navigates to the VisitBRP page used for visitor booking.
- Selects the first prisoner checkbox.
- Fills visitor ID fields and submits the booking flow.
- Interacts with search/add dialogs and selects a visit round (calculated as tomorrow's day).
- Captures screenshots at important steps and prints dialog messages to the console.

Files of interest
- `main.py` — the Playwright script (single-file automation).
- `after_first_submit.png`, `alert_screenshot.png`, `after_final_click.png` — screenshots produced by the script when running (if the script triggers them).

## Prerequisites

- Windows with PowerShell (instructions below use your default `pwsh`).
- Python 3.11 (or similar supported by Playwright/uv).
- `uv` (the project tool used in this workspace) — used here to manage the virtual env and dependencies.

If you haven't already prepared the project, run these commands from the project root (`d:\python\visit`) in PowerShell:

```powershell
# initialize project (if not yet initialized)
uv init

# add Playwright to the project and create a .venv
uv add playwright

# install Playwright browsers
uv run playwright install
```

## Run the automation

From the repository root run:

```powershell
uv run python main.py
```

This launches Chromium (by default in non-headless mode) and walks through the booking steps. The script prints dialog messages to the console when a browser alert appears and saves screenshots for debugging.

## Quick configuration

- To run headless, edit `main.py` and set `p.chromium.launch(headless=True)`.
- To change the ID values or phone number, edit these lines in `main.py`:
	- `page.fill("#idno", "4130300003031")`
	- `page.fill("#search_idno", "4130300003023")`
	- `page.fill("#mobile", "0991795649")`

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

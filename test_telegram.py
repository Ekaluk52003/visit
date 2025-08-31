#!/usr/bin/env python3
"""
Test script for Telegram bot functionality
Run this to verify your Telegram bot is working before running the main automation
"""

from telegram_helper import send_telegram_message, send_dialog_alert, send_automation_status
from datetime import datetime

def test_telegram_bot():
    """Test the Telegram bot functionality"""

    print("🧪 Testing Telegram bot functionality...")
    print("=" * 50)

    # Test 1: Basic message
    print("1. Testing basic message...")
    success1 = send_telegram_message("🤖 Hello! This is a test message from your VisitBRP automation bot.")

    # Test 2: Dialog alert
    print("2. Testing dialog alert...")
    success2 = send_dialog_alert("alert", "This is a test dialog message", datetime.now())

    # Test 3: Status message
    print("3. Testing status message...")
    success3 = send_automation_status("Started", "Testing Telegram integration")

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Basic message: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Dialog alert:  {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"   Status update: {'✅ PASS' if success3 else '❌ FAIL'}")

    if all([success1, success2, success3]):
        print("\n🎉 All tests passed! Your Telegram bot is ready to use.")
        send_automation_status("Completed", "Telegram bot test completed successfully")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        print("\nTroubleshooting:")
        print("1. Verify your bot token in config.py")
        print("2. Verify your chat ID in config.py")
        print("3. Make sure you've sent at least one message to your bot")
        print("4. Check your internet connection")

if __name__ == "__main__":
    test_telegram_bot()

#!/usr/bin/env python3
"""
Direct test of Instagram login - checks dependencies first.
"""

import sys
from pathlib import Path

# Add the instagram-upload directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "instagram-upload"))

print("🔍 Checking dependencies...")

# Check if Playwright is installed
try:
    import playwright
    print("✅ Playwright package available")
except ImportError:
    print("❌ Playwright not installed")
    print("   Run: pip install playwright")
    sys.exit(1)

# Check if async_api module is available (part of playwright)
try:
    from playwright.async_api import async_playwright
    print("✅ Playwright async_api module available")
except ImportError:
    print("❌ Playwright async_api module not available")
    print("   Make sure playwright package is fully installed")
    sys.exit(1)

# Check if dotenv is installed
try:
    import dotenv
    print("✅ dotenv package available")
except ImportError:
    print("❌ dotenv not installed")
    print("   Run: pip install python-dotenv")
    sys.exit(1)

# Check .env.instagram file
env_path = Path(".env.instagram")
if not env_path.exists():
    print("❌ .env.instagram file not found")
    print("   Copy from templates/.env.instagram.template")
    sys.exit(1)

print("\n✅ All dependencies available")
print("🚀 Starting Instagram login test...")

# Now try to import and run our login manager
try:
    from src.auth.login_manager import InstagramLoginManager

    import asyncio

    # Create manager instance
    manager = InstagramLoginManager()

    print(f"\n👤 Username: {manager.username}")
    print(f"🔐 Password length: {len(manager.password)} characters")
    print(f"🛡️  2FA Enabled: {manager.enable_2fa}")

    print("\n⚠️  IMPORTANT WARNING:")
    print("This test will open a browser and attempt to login.")
    print("If 2FA is enabled, it will pause and ask for a 6-digit code.")
    print("\nContinue? (y/n): ")

    response = input().strip().lower()
    if response != 'y':
        print("Test cancelled.")
        sys.exit(0)

    # Run the login test
    print("\nStarting login process...")

    # First try cookie login
    print("1. Trying cookie-based login...")
    cookie_success = asyncio.run(manager.login_with_cookies())

    if cookie_success:
        print("✅ Login successful with cookies!")
        sys.exit(0)

    print("2. Performing full login...")
    login_success = asyncio.run(manager.login())

    if login_success:
        print("✅ Full login successful!")
        sys.exit(0)
    else:
        print("❌ Login failed")
        print("📸 Debug screenshots saved in ./logs/")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
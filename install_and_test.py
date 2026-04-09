#!/usr/bin/env python3
"""
Installation and testing script for Instagram Upload Service.

This script:
1. Guides through Playwright installation
2. Tests the login system
3. Shows the complete 2FA flow

Created by: Sam Lead Developer
Date: 2026-04-08
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print(f"\n{text}")
    print("=" * len(text))

def run_command(command):
    """Run command and return result."""
    print(f"  Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Success")
            return True
        else:
            print(f"  ❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def check_playwright_installed():
    """Check if Playwright is installed."""
    try:
        import playwright
        print("✅ Playwright Python package is installed")
        return True
    except ImportError:
        print("❌ Playwright Python package NOT installed")
        return False

def check_dotenv_installed():
    """Check if dotenv is installed."""
    try:
        import dotenv
        print("✅ dotenv package is installed")
        return True
    except ImportError:
        print("❌ dotenv package NOT installed")
        return False

def check_browser_installed():
    """Check if Playwright browser is installed."""
    try:
        # Try to run playwright command
        result = subprocess.run(["playwright", "--version"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Playwright CLI installed: {result.stdout}")
            return True
        else:
            print("❌ Playwright CLI NOT installed")
            return False
    except Exception:
        print("❌ Playwright CLI NOT installed")
        return False

def main():
    """Main installation and testing function."""
    print_header("🚀 Instagram Upload Service - Installation & Testing")

    # Step 1: Check current state
    print_header("📋 Step 1: Current Installation Status")

    playwright_python = check_playwright_installed()
    dotenv_installed = check_dotenv_installed()
    playwright_cli = check_browser_installed()

    if playwright_python and dotenv_installed and playwright_cli:
        print("\n🎉 All dependencies already installed!")
        print("Proceeding to test...")
        return run_test()

    # Step 2: Installation guide
    print_header("📋 Step 2: Installation Guide")

    print("\n📌 Installation options:")
    print("1. Global installation (recommended for development)")
    print("2. User installation (if global fails)")
    print("3. Virtual environment (most isolated)")

    print("\n📌 Recommended commands:")

    if not playwright_python:
        print("👉 Install Playwright Python package:")
        print("   pip install playwright python-dotenv")
        print("   or: pip3 install playwright python-dotenv --user")

    if not playwright_cli:
        print("👉 Install Playwright browsers:")
        print("   playwright install chromium")
        print("   playwright install --help (for more options)")

    # Step 3: Offer to install
    print_header("📋 Step 3: Installation Attempt")

    print("\nDo you want to attempt installation now? (y/n): ")
    response = input().strip().lower()

    if response == 'y':
        print("\nAttempting installation...")

        # Try pip install
        if not playwright_python:
            success = run_command("pip install playwright python-dotenv")
            if success:
                playwright_python = True

        # Try playwright install
        if not playwright_cli and playwright_python:
            success = run_command("playwright install chromium")
            if success:
                playwright_cli = True

        # Check again
        playwright_python = check_playwright_installed()
        dotenv_installed = check_dotenv_installed()
        playwright_cli = check_browser_installed()

    # Step 4: Test if installed
    if playwright_python and dotenv_installed and playwright_cli:
        print_header("📋 Step 4: Running Test")
        return run_test()
    else:
        print_header("📋 Step 4: Manual Setup Required")
        print("\n❌ Installation incomplete. Manual steps required:")
        print("1. Install Python packages:")
        print("   pip install playwright python-dotenv")
        print("2. Install browsers:")
        print("   playwright install chromium")
        print("3. Then run test:")
        print("   python scripts/test_login.py")

        return False

def run_test():
    """Run the login test."""
    print_header("🚀 Running Instagram Login Test")

    # Check .env.instagram exists
    env_path = Path(".env.instagram")
    if not env_path.exists():
        print("❌ .env.instagram file missing")
        print("Copy from templates/.env.instagram.template")
        return False

    print("✅ .env.instagram file exists")

    # Try to import and run test
    try:
        # Add module path
        sys.path.insert(0, str(Path(__file__).parent / "instagram-upload"))

        from src.auth.login_manager import InstagramLoginManager

        import asyncio

        # Create instance
        manager = InstagramLoginManager()

        print(f"\n👤 Username: {manager.username}")
        print(f"🔐 Password length: {len(manager.password)} characters")
        print(f"🛡️  2FA Enabled: {manager.enable_2fa}")

        print("\n⚠️  IMPORTANT WARNING:")
        print("This test will:")
        print("1. Open a real browser window")
        print("2. Attempt to login to Instagram")
        print("3. PAUSE and ask for 6-digit 2FA code")
        print("4. Save session cookies")

        print("\n📱 You will need to:")
        print("1. Watch for 2FA code on your device")
        print("2. Enter 6-digit code when prompted")
        print("3. Code expires in 60 seconds")

        print("\nContinue? (y/n): ")
        response = input().strip().lower()

        if response != 'y':
            print("Test cancelled.")
            return False

        # Run test
        print("\n🚀 Starting test...")

        # Try cookie login first
        print("1. Checking saved cookies...")
        cookie_success = asyncio.run(manager.login_with_cookies())

        if cookie_success:
            print("✅ Login successful with cookies!")
            print("🎉 Test completed!")
            return True

        # Full login
        print("2. Performing full login...")
        login_success = asyncio.run(manager.login())

        if login_success:
            print("✅ Full login successful!")
            print("💾 Cookies saved for future use")
            print("🎉 Test completed!")
            return True
        else:
            print("❌ Login failed")
            print("📸 Debug screenshots saved in ./logs/")
            print("💀 Test failed")
            return False

    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()

    if success:
        print_header("🎉 SUCCESS!")
        print("\nInstagram Login System is WORKING!")
        print("Next steps:")
        print("1. Review ./logs/ for screenshots")
        print("2. Check ./data/instagram_cookies.json")
        print("3. Continue with Day 2 development")
        sys.exit(0)
    else:
        print_header("💀 SETUP INCOMPLETE")
        print("\nInstallation or test failed.")
        print("Next steps:")
        print("1. Install dependencies manually")
        print("2. Run: python scripts/test_login.py")
        print("3. Enter 6-digit 2FA code when prompted")
        sys.exit(1)
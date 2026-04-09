#!/usr/bin/env python3
"""
Auto-install and test script for Instagram Upload Service.
This version doesn't require interactive input.

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

def run_command(command, show_output=True):
    """Run command and return result."""
    print(f"  Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Success")
            if show_output and result.stdout:
                print(f"  Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"  ❌ Failed")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}...")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def check_playwright():
    """Check if Playwright is installed."""
    try:
        import playwright
        print("✅ Playwright Python package is installed")
        return True
    except ImportError:
        print("❌ Playwright Python package NOT installed")
        return False

def check_dotenv():
    """Check if dotenv is installed."""
    try:
        import dotenv
        print("✅ dotenv package is installed")
        return True
    except ImportError:
        print("❌ dotenv package NOT installed")
        return False

def check_browser():
    """Check if Playwright browser is installed."""
    try:
        result = subprocess.run(["playwright", "--version"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Playwright CLI installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Playwright CLI NOT installed")
            return False
    except Exception:
        print("❌ Playwright CLI NOT installed")
        return False

def main():
    """Main auto-installation function."""
    print_header("🚀 Instagram Upload Service - Auto Installation & Test")

    # Step 1: Check current state
    print_header("📋 Step 1: Checking Dependencies")

    playwright_ok = check_playwright()
    dotenv_ok = check_dotenv()
    browser_ok = check_browser()

    # Step 2: Install missing dependencies
    if not playwright_ok or not dotenv_ok:
        print_header("📋 Step 2: Installing Python Packages")

        print("\nAttempting to install Playwright and dotenv...")

        # Try different installation methods
        methods = [
            "pip install playwright python-dotenv",
            "pip3 install playwright python-dotenv",
            "python -m pip install playwright python-dotenv",
            "python3 -m pip install playwright python-dotenv"
        ]

        installed = False
        for method in methods:
            print(f"\nTrying: {method}")
            if run_command(method, show_output=False):
                installed = True
                break

        if installed:
            print("\n✅ Python packages installation successful")
            playwright_ok = check_playwright()
            dotenv_ok = check_dotenv()
        else:
            print("\n❌ Python packages installation failed")
            print("Please install manually:")
            print("pip install playwright python-dotenv")

    # Step 3: Install browser
    if playwright_ok and not browser_ok:
        print_header("📋 Step 3: Installing Browser")

        print("\nInstalling Chromium browser...")
        if run_command("playwright install chromium"):
            browser_ok = check_browser()
        else:
            print("❌ Browser installation failed")
            print("Try: playwright install chromium")

    # Step 4: Check .env file
    print_header("📋 Step 4: Checking Configuration")

    env_path = Path(".env.instagram")
    if not env_path.exists():
        print("❌ .env.instagram file missing")

        # Check if template exists
        template_path = Path("templates/.env.instagram.template")
        if template_path.exists():
            print("✅ Template found, creating .env.instagram...")
            try:
                import shutil
                shutil.copy(template_path, env_path)
                print("✅ .env.instagram created from template")
                print("⚠️  Remember to edit with real credentials")
            except Exception as e:
                print(f"❌ Error creating file: {e}")
        else:
            print("❌ Template not found at templates/.env.instagram.template")
            return False
    else:
        print("✅ .env.instagram file exists")

    # Step 5: Run test if everything is ready
    if playwright_ok and dotenv_ok and browser_ok:
        print_header("📋 Step 5: Ready for Testing")

        print("\n🎉 All dependencies installed!")
        print("\n📋 To test the login system:")
        print("1. Edit .env.instagram with real credentials")
        print("2. Run: python scripts/test_login.py")
        print("3. Enter 6-digit 2FA code when prompted")
        print("\n📋 Test command:")
        print("cd instagram-upload && python scripts/test_login.py")

        # Show what the test will do
        print("\n📋 What the test does:")
        print("1. Opens browser and goes to Instagram")
        print("2. Logs in with credentials from .env.instagram")
        print("3. PAUSES for 2FA code input (6 digits)")
        print("4. Saves session cookies for future use")

        return True
    else:
        print_header("📋 Step 5: Installation Incomplete")

        print("\n❌ Some dependencies missing:")
        if not playwright_ok:
            print("- Playwright Python package")
        if not dotenv_ok:
            print("- python-dotenv package")
        if not browser_ok:
            print("- Playwright browser")

        print("\n📋 Manual installation required:")
        print("1. pip install playwright python-dotenv")
        print("2. playwright install chromium")
        print("3. Then run test: python scripts/test_login.py")

        return False

if __name__ == "__main__":
    success = main()

    print_header("📋 Summary")
    if success:
        print("\n✅ Installation guide completed")
        print("📁 Next: Edit .env.instagram and run test")
        sys.exit(0)
    else:
        print("\n❌ Installation incomplete")
        print("📁 Please install dependencies manually")
        sys.exit(1)
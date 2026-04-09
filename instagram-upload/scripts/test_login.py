#!/usr/bin/env python3
"""
Test script for Instagram Login Manager.

This script tests the complete login flow including 2FA handling.
Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for module import
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth.login_manager import InstagramLoginManager, main


async def test_login_flow():
    """Test the complete login flow."""
    print("🚀 Testing Instagram Login Manager")
    print("==================================")

    # Check if .env.instagram exists
    if not Path("../.env.instagram").exists():
        print("❌ .env.instagram not found")
        print("   Run: cp templates/.env.instagram.template .env.instagram")
        print("   Then edit with real credentials")
        return False

    # Create login manager
    try:
        manager = InstagramLoginManager()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

    print(f"✅ Configuration loaded")
    print(f"👤 Username: {manager.username}")
    print(f"🔐 Password configured: {'*' * len(manager.password)}")
    print(f"🛡️  2FA Enabled: {manager.enable_2fa}")
    print()

    # Test cookie login first
    print("1. Testing cookie-based login...")
    cookie_success = await manager.login_with_cookies()

    if cookie_success:
        print("✅ Login successful with saved cookies")
        print("🎉 Test completed successfully!")
        return True

    print("🔄 Cookies not found or expired, testing full login...")

    # Test full login
    print("2. Testing full login process...")
    print("⚠️  IMPORTANT: If 2FA is required, the application will pause")
    print("   and request a 6-digit code from you.")
    print()

    login_success = await manager.login()

    if login_success:
        print("✅ Full login successful")
        print("💾 Cookies saved for future use")
        print("🎉 Test completed successfully!")
        return True
    else:
        print("❌ Login failed")
        print("📸 Debug screenshots saved in ./logs/")
        print("💀 Test failed")
        return False


def run_tests():
    """Run all tests."""
    print("Instagram Login Manager Integration Test")
    print("========================================")
    print()

    # Run async test
    success = asyncio.run(test_login_flow())

    if success:
        print()
        print("✨ ALL TESTS PASSED!")
        print("📁 Next steps:")
        print("1. Review logs in ./logs/")
        print("2. Check cookies in ./data/instagram_cookies.json")
        print("3. Continue with upload module development")
        return 0
    else:
        print()
        print("💀 TESTS FAILED!")
        print("📁 Debug steps:")
        print("1. Check .env.instagram configuration")
        print("2. Review screenshots in ./logs/")
        print("3. Test manually in browser")
        return 1


if __name__ == "__main__":
    exit(run_tests())
#!/usr/bin/env python3
"""
Example authentication flow showing integration between components.

This demonstrates how BrowserService, LoginManager, and CookieManager
work together for Instagram authentication.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def example_without_2fa():
    """Example authentication flow without 2FA (mocked)."""
    print("🔐 Example: Authentication Flow Without 2FA")
    print("=" * 50)

    try:
        from src.auth.browser_service import BrowserService, BrowserConfig
        from src.auth.login_manager import InstagramLoginManager
        from src.auth.cookie_manager import CookieManager

        print("✅ All modules imported successfully")

        # Create configuration
        config = BrowserConfig(
            headless=True,  # Headless for example
            slow_mo=0,      # No delay for example
            timeout=10000   # 10 second timeout
        )

        print("\n1. Creating components...")
        browser_service = BrowserService(config)
        login_manager = InstagramLoginManager()
        cookie_manager = CookieManager()

        print(f"   • BrowserService created with config: {config.browser_type.value}")
        print(f"   • LoginManager created for user: {login_manager.username}")
        print(f"   • CookieManager using path: {cookie_manager.cookies_path}")

        print("\n2. Checking for existing session...")
        if cookie_manager.has_valid_session():
            username = cookie_manager.get_session_username()
            print(f"   ✅ Valid session found for user: {username}")
            print("   Session would be used instead of full login")
        else:
            print("   ❌ No valid session found")
            print("   Full login would be required")

        print("\n3. Example cookie operations...")

        # Example cookies
        example_cookies = [
            {
                'name': 'sessionid',
                'value': 'example_session_value',
                'domain': '.instagram.com',
                'path': '/',
                'expires': 1234567890.0,
                'httpOnly': True,
                'secure': True
            }
        ]

        # Save example cookies
        success = cookie_manager.save_cookies(example_cookies, "example_user")
        if success:
            print("   ✅ Example cookies saved")

            # Load them back
            loaded_cookies, session_info = cookie_manager.load_cookies()
            if loaded_cookies and session_info:
                print(f"   ✅ Cookies loaded for: {session_info.username}")
                print(f"   • Cookie count: {len(loaded_cookies)}")
                print(f"   • Session valid: {session_info.is_valid}")

        print("\n4. Cleanup...")
        cookie_manager.clear_all()
        print("   ✅ All session data cleared")

        print("\n🎉 Example completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def example_with_2fa():
    """Example showing 2FA handling (mocked)."""
    print("\n🔐 Example: 2FA Authentication Flow")
    print("=" * 50)

    try:
        from src.auth.login_manager import InstagramLoginManager

        print("1. Creating LoginManager with 2FA enabled...")

        # Mock environment with 2FA enabled
        with open(".env.instagram.example", "w") as f:
            f.write("""INSTAGRAM_USERNAME=test_user
INSTAGRAM_PASSWORD=test_password
INSTAGRAM_ENABLE_2FA=true
PLAYWRIGHT_HEADLESS=true
""")

        # Load the example env file
        import dotenv
        dotenv.load_dotenv(".env.instagram.example")

        manager = InstagramLoginManager()

        print(f"   • User: {manager.username}")
        print(f"   • 2FA enabled: {manager.enable_2fa}")

        print("\n2. Simulating 2FA code input...")

        # Mock interactive input
        import builtins
        original_input = builtins.input

        def mock_input(prompt):
            print(f"   [MOCK INPUT] {prompt}")
            return "123456"  # Mock 2FA code

        builtins.input = mock_input

        try:
            # This would normally get called during login
            print("   Simulating 2FA requirement...")
            print("   [SYSTEM]: 🔢 TWO-FACTOR AUTHENTICATION (2FA) REQUIRED")
            print("   [SYSTEM]: Please enter the 6-digit code from your device")

            # Call the 2FA input method
            code = manager._get_two_factor_code_from_user()
            print(f"   ✅ Received 2FA code: {'*' * 6}")

            # Example of 2FA code validation
            from datetime import datetime
            from src.auth.login_manager import TwoFactorCode

            try:
                two_factor_code = TwoFactorCode(code=code, timestamp=datetime.now())
                print(f"   ✅ 2FA code validated successfully")
                print(f"   • Code length: {len(two_factor_code.code)} digits")
                print(f"   • Timestamp: {two_factor_code.timestamp}")
            except ValueError as e:
                print(f"   ❌ 2FA code validation failed: {e}")

        finally:
            # Restore original input
            builtins.input = original_input

        # Cleanup
        Path(".env.instagram.example").unlink(missing_ok=True)

        print("\n🎉 2FA example completed!")
        return True

    except Exception as e:
        print(f"❌ 2FA example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_imports():
    """Check that all required imports work."""
    print("🔍 Checking module imports...")
    print("=" * 50)

    modules = [
        ("BrowserService", "src.auth.browser_service"),
        ("LoginManager", "src.auth.login_manager"),
        ("CookieManager", "src.auth.cookie_manager"),
    ]

    all_imported = True

    for module_name, import_path in modules:
        try:
            # Dynamic import
            import importlib
            module = importlib.import_module(import_path)
            print(f"✅ {module_name}: Import successful")
        except ImportError as e:
            print(f"❌ {module_name}: Import failed - {e}")
            all_imported = False
        except Exception as e:
            print(f"❌ {module_name}: Error - {e}")
            all_imported = False

    return all_imported

def check_environment():
    """Check environment configuration."""
    print("\n🔧 Checking environment configuration...")
    print("=" * 50)

    required_vars = ["INSTAGRAM_USERNAME", "INSTAGRAM_PASSWORD"]
    optional_vars = ["INSTAGRAM_ENABLE_2FA", "PLAYWRIGHT_HEADLESS"]

    print("Required variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value and value not in ["your_instagram_username_here", "your_instagram_password_here"]:
            masked = value[:3] + "..." + value[-3:] if len(value) > 6 else "***"
            print(f"  ✅ {var}: {masked}")
        elif value:
            print(f"  ⚠️  {var}: Using placeholder value - needs to be configured")
        else:
            print(f"  ❌ {var}: Not set")

    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set (using default)")

async def main():
    """Main example function."""
    print("🚀 Instagram Upload Service - Authentication Example")
    print("=" * 60)

    # Check imports
    if not check_imports():
        print("\n❌ Some imports failed. Please check installation.")
        return False

    # Check environment
    check_environment()

    # Run examples
    print("\n" + "=" * 60)
    success1 = await example_without_2fa()

    print("\n" + "=" * 60)
    success2 = await example_with_2fa()

    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)

    if success1 and success2:
        print("✅ All examples completed successfully!")
        print("\n🎯 Next steps:")
        print("1. Configure .env.instagram with your credentials")
        print("2. Install Playwright: pip install playwright")
        print("3. Install browser: playwright install chromium")
        print("4. Run tests: python run_tests.py")
        print("5. Try actual login: python scripts/test_instagram_login.py")
        return True
    else:
        print("❌ Some examples failed")
        return False

if __name__ == "__main__":
    # Run async main
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
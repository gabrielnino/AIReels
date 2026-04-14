"""
Instagram Login Manager with Two-Factor Authentication (2FA) support.

This module handles the complete login process to Instagram using Playwright,
including the handling of 2FA with manual code input when required.

IMPORTANT: The application will pause and request manual input for 2FA codes.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import asyncio
import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv

# Load Instagram configuration
load_dotenv('.env.instagram')


@dataclass
class LoginCredentials:
    """Credentials for Instagram login."""
    username: str
    password: str
    enable_2fa: bool = True

    def __post_init__(self):
        """Validate credentials after initialization."""
        if not self.username or not self.password:
            raise ValueError("Username and password must be provided")
        if len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(self.password) < 6:
            raise ValueError("Password must be at least 6 characters")


@dataclass
class TwoFactorCode:
    """Two-factor authentication code."""
    code: str
    timestamp: datetime

    def __post_init__(self):
        """Validate 2FA code."""
        if len(self.code) != 6:
            raise ValueError("2FA code must be exactly 6 digits")
        if not self.code.isdigit():
            raise ValueError("2FA code must contain only digits")

        # Check if code is expired (typically 60 seconds)
        age = (datetime.now() - self.timestamp).total_seconds()
        if age > 60:
            raise ValueError("2FA code has expired (max 60 seconds)")


class InstagramLoginManager:
    """Manages Instagram login process with 2FA support."""

    def __init__(self):
        """Initialize login manager with configuration."""
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.enable_2fa = os.getenv('INSTAGRAM_ENABLE_2FA', 'true').lower() == 'true'
        self.cookies_path = os.getenv('INSTAGRAM_COOKIES_PATH', './data/instagram_cookies.json')
        self.headless = os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true'
        self.slow_mo = int(os.getenv('PLAYWRIGHT_SLOW_MO', '100'))
        self.timeout = int(os.getenv('PLAYWRIGHT_TIMEOUT', '30000'))

        # Validate configuration
        self._validate_configuration()

        # Initialize credentials object
        self.credentials = LoginCredentials(
            username=self.username,
            password=self.password,
            enable_2fa=self.enable_2fa
        )

    def _validate_configuration(self) -> None:
        """Validate that all required configuration is present."""
        if not self.username or self.username == 'your_instagram_username_here':
            raise ConfigurationError("INSTAGRAM_USERNAME not configured in .env.instagram")

        if not self.password or self.password == 'your_instagram_password_here':
            raise ConfigurationError("INSTAGRAM_PASSWORD not configured in .env.instagram")

        # Ensure cookies directory exists
        Path(self.cookies_path).parent.mkdir(parents=True, exist_ok=True)

    async def login(self) -> bool:
        """Perform complete login process with 2FA support.

        Returns:
            bool: True if login successful, False otherwise

        Raises:
            ConfigurationError: If credentials are not configured
            AuthenticationError: If login fails
            TwoFactorRequiredError: If 2FA is required but not handled
        """
        print("🔐 Starting Instagram login process...")
        print(f"👤 User: {self.credentials.username}")

        from playwright.async_api import async_playwright

        try:
            async with async_playwright() as p:
                # Launch browser with configured settings
                browser = await p.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )

                # Create browser context
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                page = await context.new_page()

                try:
                    # Navigate to Instagram
                    print("🌐 Navigating to Instagram...")
                    await page.goto('https://www.instagram.com/')
                    await page.wait_for_timeout(2000)

                    # Handle cookies popup if present
                    await self._handle_cookies_popup(page)

                    # Perform initial login
                    print("📝 Performing initial login...")
                    login_success = await self._perform_initial_login(page)

                    if login_success:
                        print("✅ Login successful without 2FA")
                        await self._save_session_cookies(context)
                        await browser.close()
                        return True

                    # Check for 2FA requirement
                    print("🔍 Checking for 2FA requirement...")
                    if await self._is_two_factor_required(page):
                        if not self.credentials.enable_2fa:
                            raise TwoFactorRequiredError("2FA required but not enabled in configuration")

                        print("⚠️  Two-factor authentication (2FA) required")
                        two_factor_success = await self._handle_two_factor_auth(page)

                        if two_factor_success:
                            print("✅ 2FA authentication successful")
                            await self._save_session_cookies(context)
                            await browser.close()
                            return True
                        else:
                            print("❌ 2FA authentication failed")
                            await browser.close()
                            return False

                    # Check for login errors
                    error_message = await self._get_login_error(page)
                    if error_message:
                        print(f"❌ Login error: {error_message}")
                        await self._save_debug_screenshot(page, "login_error")
                        await browser.close()
                        raise AuthenticationError(error_message)

                    # Unknown state
                    print("❌ Login failed - unknown state")
                    await self._save_debug_screenshot(page, "login_unknown_state")
                    await browser.close()
                    return False

                except Exception as e:
                    print(f"❌ Exception during login: {e}")
                    await self._save_debug_screenshot(page, "login_exception")
                    await browser.close()
                    raise AuthenticationError(f"Login process exception: {e}")

        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            raise BrowserError(f"Browser initialization failed: {e}")

    async def _handle_cookies_popup(self, page) -> None:
        """Handle cookies acceptance popup if present."""
        try:
            accept_button = page.get_by_role("button", name="Allow all cookies")
            if await accept_button.is_visible(timeout=3000):
                await accept_button.click()
                print("✅ Cookies accepted")
                await page.wait_for_timeout(1000)
        except:
            pass  # No cookies popup present

    async def _perform_initial_login(self, page) -> bool:
        """Perform initial login with username and password."""
        try:
            # Fill username and password fields
            await page.fill('input[name="username"]', self.credentials.username)
            await page.fill('input[name="password"]', self.credentials.password)

            # Click login button
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)

            # Check if login was successful (no 2FA required)
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
                return True
            except:
                return False  # Might require 2FA

        except Exception as e:
            print(f"❌ Initial login failed: {e}")
            return False

    async def _is_two_factor_required(self, page) -> bool:
        """Check if two-factor authentication is required."""
        try:
            await page.wait_for_selector('input[name="verificationCode"]', timeout=5000)
            return True
        except:
            return False

    async def _handle_two_factor_auth(self, page) -> bool:
        """Handle two-factor authentication with manual code input.

        IMPORTANT: This function will pause and request manual input from the user.
        """
        print("")
        print("🔢 TWO-FACTOR AUTHENTICATION (2FA) REQUIRED")
        print("===========================================")
        print("A 6-digit code has been sent to your device.")
        print("")
        print("Please enter the code below:")
        print("1. Check your authentication app or SMS")
        print("2. Enter the 6-digit code")
        print("3. Press Enter")
        print("")

        # Get 2FA code from user
        code = self._get_two_factor_code_from_user()

        # Create 2FA code object with timestamp
        two_factor_code = TwoFactorCode(code=code, timestamp=datetime.now())

        print(f"🔑 Entering 2FA code: {'*' * 6}")

        # Fill 2FA code field
        await page.fill('input[name="verificationCode"]', two_factor_code.code)

        # Find and click confirmation button
        confirm_button = page.locator('button:has-text("Confirm")').first
        await confirm_button.click()

        await page.wait_for_timeout(3000)

        # Verify 2FA was successful
        try:
            await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
            print("✅ 2FA verification successful")
            return True
        except:
            # Check for 2FA error
            try:
                error_elem = page.locator('[data-testid="error-alert"]').first
                error_text = await error_elem.text_content(timeout=2000)
                print(f"❌ 2FA error: {error_text}")
            except:
                print("❌ 2FA code incorrect or expired")

            await self._save_debug_screenshot(page, "2fa_error")
            return False

    def _get_two_factor_code_from_user(self) -> str:
        """Get 2FA code from user input.

        In non-interactive environments, reads from INSTAGRAM_2FA_CODE env var.
        """
        if sys.stdin.isatty():
            # Interactive terminal - request input
            code = input("📱 2FA Code (6 digits): ").strip()
        else:
            # Non-interactive - read from environment
            code = os.getenv('INSTAGRAM_2FA_CODE', '').strip()
            if not code:
                raise TwoFactorInputError(
                    "Cannot request 2FA code in non-interactive mode. "
                    "Set INSTAGRAM_2FA_CODE in .env.instagram."
                )

        return code

    async def _get_login_error(self, page) -> Optional[str]:
        """Get login error message if present."""
        try:
            error_element = page.locator('p[id="slfErrorAlert"]').first
            error_text = await error_element.text_content(timeout=2000)
            return error_text
        except:
            return None

    async def _save_session_cookies(self, context) -> None:
        """Save session cookies for future use."""
        cookies = await context.cookies()

        with open(self.cookies_path, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"💾 Session cookies saved to: {self.cookies_path}")

    async def _save_debug_screenshot(self, page, filename: str) -> None:
        """Save debug screenshot for troubleshooting."""
        screenshot_path = f"./logs/{filename}.png"
        Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)

        await page.screenshot(path=screenshot_path)
        print(f"📸 Debug screenshot saved: {screenshot_path}")

    async def login_with_cookies(self) -> bool:
        """Attempt login using saved cookies.

        Returns:
            bool: True if login successful with cookies, False otherwise
        """
        print("🔐 Attempting login with saved cookies...")

        if not Path(self.cookies_path).exists():
            print("❌ No saved cookies found")
            return False

        from playwright.async_api import async_playwright

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)

                # Load cookies from file
                with open(self.cookies_path, 'r') as f:
                    cookies = json.load(f)

                context = await browser.new_context()
                await context.add_cookies(cookies)

                page = await context.new_page()

                # Navigate to Instagram
                await page.goto('https://www.instagram.com/')
                await page.wait_for_timeout(2000)

                # Check if already logged in
                try:
                    await page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
                    print("✅ Already logged in with cookies")
                    await browser.close()
                    return True
                except:
                    print("❌ Cookies expired or invalid")
                    await browser.close()
                    return False

        except Exception as e:
            print(f"❌ Cookie login failed: {e}")
            return False


# Exception classes for specific error types
class ConfigurationError(Exception):
    """Error in configuration."""
    pass

class AuthenticationError(Exception):
    """Error during authentication."""
    pass

class TwoFactorRequiredError(Exception):
    """2FA is required but not available."""
    pass

class TwoFactorInputError(Exception):
    """Error getting 2FA code input."""
    pass

class BrowserError(Exception):
    """Error with browser setup."""
    pass


# Main function for testing
async def main():
    """Main function for testing login manager."""
    manager = InstagramLoginManager()

    print("Instagram Login Manager Test")
    print("============================")

    # First try with cookies
    if await manager.login_with_cookies():
        print("✅ Login successful with cookies")
        return True

    # If cookies fail, perform full login
    print("🔄 Cookies failed, performing full login...")
    success = await manager.login()

    if success:
        print("🎉 Login test successful")
        return True
    else:
        print("💀 Login test failed")
        return False


if __name__ == "__main__":
    # Run async main function
    success = asyncio.run(main())
    exit(0 if success else 1)
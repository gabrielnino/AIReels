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
            print("🔍 Looking for login form...")

            # Lista de selectores alternativos para campos de login
            # ACTUALIZADO basado en diagnóstico: Instagram ahora usa name="email" y name="pass"
            username_selectors = [
                'input[name="email"]',  # ¡NUEVO! Instagram ahora usa "email" no "username"
                'input[name="username"]',  # Mantener por compatibilidad
                'input[aria-label="Phone number, username, or email"]',
                'input[aria-label*="username"]',
                'input[aria-label*="email"]',
                'input[placeholder*="username"]',
                'input[placeholder*="Username"]',
                'input[placeholder*="email"]',
                'input[placeholder*="Email"]',
                'input[type="text"]:first-of-type',
                'input:first-of-type'
            ]

            password_selectors = [
                'input[name="pass"]',  # ¡NUEVO! Instagram ahora usa "pass" no "password"
                'input[name="password"]',  # Mantener por compatibilidad
                'input[aria-label="Password"]',
                'input[aria-label*="password"]',
                'input[placeholder*="password"]',
                'input[placeholder*="Password"]',
                'input[type="password"]',
                'input:nth-of-type(2)'
            ]

            login_button_selectors = [
                'button[type="submit"]',
                'div[role="button"]:has-text("Log in")',
                'button:has-text("Log in")',
                'button:has-text("Log In")'
            ]

            # Intentar encontrar y llenar username con selectores alternativos
            username_filled = False
            for selector in username_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.fill(selector, self.credentials.username)
                    print(f"✅ Username field found with: {selector}")
                    username_filled = True
                    break
                except:
                    continue

            if not username_filled:
                print("❌ Could not find username field")
                return False

            # Intentar encontrar y llenar password con selectores alternativos
            password_filled = False
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.fill(selector, self.credentials.password)
                    print(f"✅ Password field found with: {selector}")
                    password_filled = True
                    break
                except:
                    continue

            if not password_filled:
                print("❌ Could not find password field")
                return False

            # Intentar hacer click en botón de login con selectores alternativos
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    print(f"✅ Login button found with: {selector}")
                    login_clicked = True
                    break
                except:
                    continue

            if not login_clicked:
                print("❌ Could not find login button")
                return False

            await page.wait_for_timeout(5000)  # Wait for login to process

            # Check if login was successful (no 2FA required) with multiple selectors
            success_selectors = [
                'svg[aria-label="Home"]',
                'a[href="/"] svg',  # Home icon alternative
                'div[data-testid="primary-nav"]',  # Main navigation
                'a[href*="direct"]',  # Messages link
                'nav'  # Any navigation element
            ]

            for selector in success_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=10000)
                    print(f"✅ Login successful - detected with: {selector}")
                    return True
                except:
                    continue

            print("⚠️  Login status uncertain - might require 2FA or have issues")
            return False  # Might require 2FA

        except Exception as e:
            print(f"❌ Initial login failed: {e}")
            return False

    async def _is_two_factor_required(self, page) -> bool:
        """Check if two-factor authentication is required."""
        print("🔍 Checking for 2FA requirement...")

        # Multiple selectors for 2FA code input - expanded for Instagram variations
        two_factor_selectors = [
            'input[name="verificationCode"]',
            'input[name="twoFactorAuthenticationCode"]',
            'input[name="2faCode"]',
            'input[name="security_code"]',
            'input[name="securityCode"]',
            'input[name="code"]',
            'input[name="Code"]',
            'input[name="twoFactorCode"]',
            'input[name="totpCode"]',
            'input[name="otpCode"]',
            'input[name="authenticatorCode"]',
            'input[placeholder*="code"]',
            'input[placeholder*="Code"]',
            'input[placeholder*="security code"]',
            'input[placeholder*="Security code"]',
            'input[placeholder*="6-digit code"]',
            'input[placeholder*="6 digit code"]',
            'input[placeholder*="Authentication code"]',
            'input[placeholder*="authentication code"]',
            'input[aria-label*="code"]',
            'input[aria-label*="Code"]',
            'input[aria-label*="security code"]',
            'input[aria-label*="Security code"]',
            'input[aria-label*="authentication code"]',
            'input[aria-label*="Authentication code"]',
            'input[type="text"][maxlength="6"]',
            'input[type="text"][maxlength="7"]',
            'input[type="text"][minlength="6"]',
            'input[type="text"][minlength="6"][maxlength="6"]',
            'input[type="text"]:last-of-type',
            'input:last-of-type',
            'input[autocomplete="one-time-code"]',  # Standard for OTP fields
            'input[inputmode="numeric"]',  # For numeric input
            'input[pattern="[0-9]*"]'  # Pattern for numbers only
        ]

        for selector in two_factor_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                print(f"✅ 2FA required - detected with: {selector}")
                return True
            except:
                continue

        print("❌ No 2FA requirement detected")
        return False

    async def _handle_two_factor_auth(self, page) -> bool:
        """Handle two-factor authentication.

        IMPORTANT: If automatic entry fails, waits for manual input.
        """
        print("")
        print("🔢 TWO-FACTOR AUTHENTICATION (2FA) REQUIRED")
        print("===========================================")
        print("A 6-digit code has been sent to your device.")
        print("")
        print("OPTION 1: Automatic entry (if field is found)")
        print("OPTION 2: Manual entry (enter code in browser)")
        print("")

        # Try automatic entry first
        auto_success = await self._try_automatic_2fa_entry(page)

        if auto_success:
            print("✅ Automatic 2FA entry successful")
            # Handle "Trust this device" after automatic entry
            trust_device_handled = await self._handle_trust_this_device(page)
            if trust_device_handled:
                print("✅ 'Trust this device' handled successfully")
            return True

        # If automatic entry fails, wait for manual entry
        print("⚠️  Automatic entry failed - waiting for MANUAL entry")
        print("📱 Please enter the 2FA code manually in the browser")
        print("⏱️  Waiting 60 seconds for manual entry...")

        manual_success = await self._wait_for_manual_2fa_entry(page)

        if manual_success:
            print("✅ Manual 2FA entry detected")
            # Handle "Trust this device" after manual entry
            trust_device_handled = await self._handle_trust_this_device(page)
            if trust_device_handled:
                print("✅ 'Trust this device' handled successfully")
            return True

        print("❌ 2FA failed - no code entered")
        return False

    async def _try_automatic_2fa_entry(self, page) -> bool:
        """Try to automatically enter 2FA code."""
        # Get 2FA code from user/env
        code = self._get_two_factor_code_from_user()

        # Create 2FA code object with timestamp
        two_factor_code = TwoFactorCode(code=code, timestamp=datetime.now())

        print(f"🔑 Trying automatic 2FA entry with code: {'*' * 6}")

        # Fill 2FA code field with alternative selectors
        print("🔍 Looking for 2FA code input field...")

        two_factor_selectors = [
            'input[name="verificationCode"]',
            'input[name="twoFactorAuthenticationCode"]',
            'input[name="2faCode"]',
            'input[name="security_code"]',
            'input[name="securityCode"]',
            'input[name="code"]',
            'input[name="Code"]',
            'input[name="twoFactorCode"]',
            'input[name="totpCode"]',
            'input[name="otpCode"]',
            'input[name="authenticatorCode"]',
            'input[placeholder*="code"]',
            'input[placeholder*="Code"]',
            'input[placeholder*="security code"]',
            'input[placeholder*="Security code"]',
            'input[placeholder*="6-digit code"]',
            'input[placeholder*="6 digit code"]',
            'input[placeholder*="Authentication code"]',
            'input[placeholder*="authentication code"]',
            'input[aria-label*="code"]',
            'input[aria-label*="Code"]',
            'input[aria-label*="security code"]',
            'input[aria-label*="Security code"]',
            'input[aria-label*="authentication code"]',
            'input[aria-label*="Authentication code"]',
            'input[type="text"][maxlength="6"]',
            'input[type="text"][maxlength="7"]',
            'input[type="text"][minlength="6"]',
            'input[type="text"][minlength="6"][maxlength="6"]',
            'input[type="text"]:last-of-type',
            'input:last-of-type',
            'input[autocomplete="one-time-code"]',
            'input[inputmode="numeric"]',
            'input[pattern="[0-9]*"]'
        ]

        code_filled = False
        for selector in two_factor_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, two_factor_code.code)
                print(f"✅ 2FA code field found with: {selector}")
                code_filled = True
                break
            except:
                continue

        if not code_filled:
            print("❌ Could not find 2FA code input field with any selector")
            print("📸 Taking screenshot for debugging...")
            await self._save_debug_screenshot(page, "2fa_input_not_found")

            # Intentar una estrategia alternativa: buscar cualquier input que parezca ser para códigos
            print("🔍 Trying alternative strategy: looking for any input that could be for 2FA...")

            # Buscar inputs con type="text" y maxlength entre 6 y 8
            all_inputs = await page.query_selector_all('input[type="text"]')
            for input_elem in all_inputs:
                try:
                    maxlength = await input_elem.get_attribute('maxlength')
                    if maxlength and maxlength.isdigit() and 6 <= int(maxlength) <= 8:
                        print(f"⚠️  Found input with maxlength={maxlength}, trying to fill 2FA code")
                        await input_elem.fill(two_factor_code.code)
                        code_filled = True
                        print("✅ Filled 2FA code using maxlength detection")
                        break
                except:
                    continue

            if not code_filled:
                print("❌ Still could not find 2FA input field")
                return False

        # Find and click confirmation button with alternative selectors
        # Instagram puede usar diferentes textos: Confirm, Submit, Verify, Continue, etc.
        # DEBUG ACTUAL: Instagram está usando "Continue" para 2FA
        confirm_button_selectors = [
            'button:has-text("Continue")',      # Instagram usa "Continue" para 2FA
            'button:has-text("continue")',
            'button:has-text("Continue"):not(:disabled)',
            'div[role="button"]:has-text("Continue")',
            'button:has-text("Confirm")',
            'button:has-text("confirm")',
            'button:has-text("Submit")',
            'button:has-text("submit")',
            'button:has-text("Verify")',
            'button:has-text("verify")',
            'button:has-text("Next")',
            'button:has-text("next")',
            'button:has-text("Done")',
            'button:has-text("done")',
            'button:has-text("Log In")',
            'button:has-text("Login")',
            'button:has-text("Sign In")',
            'button[type="submit"]',
            'button[type="submit"]:not(:disabled)',
            'div[role="button"]:has-text("Confirm")',
            'div[role="button"]:has-text("Submit")',
            'div[role="button"]:has-text("Verify")',
            'div[role="button"]:has-text("Continue")',
            'input[type="submit"]',
            'input[type="submit"]:not(:disabled)',
            'button:enabled',  # Cualquier botón habilitado
            'button'  # Último recurso: cualquier botón
        ]

        confirm_clicked = False
        for selector in confirm_button_selectors:
            try:
                confirm_button = page.locator(selector).first
                await confirm_button.click()
                print(f"✅ Confirmation button found with: {selector}")
                confirm_clicked = True
                break
            except:
                continue

        if not confirm_clicked:
            print("❌ Could not find confirmation button")
            return False

        await page.wait_for_timeout(3000)

        # Check for "Trust this device" or similar option after 2FA
        trust_device_handled = await self._handle_trust_this_device(page)
        if trust_device_handled:
            print("✅ 'Trust this device' handled successfully")

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

    async def _wait_for_manual_2fa_entry(self, page) -> bool:
        """Wait for user to manually enter 2FA code in browser.

        Returns:
            bool: True if login successful after manual entry, False otherwise
        """
        print("⏳ Waiting for manual 2FA code entry...")
        print("📱 User should enter code in browser and click Continue/Confirm")

        try:
            # Wait up to 60 seconds for user to manually enter code and submit
            for i in range(60):
                # Check if we're logged in (home icon appears)
                try:
                    await page.wait_for_selector('svg[aria-label="Home"]', timeout=1000)
                    print(f"✅ Login successful after manual 2FA entry (waited {i+1}s)")
                    return True
                except:
                    pass

                # Check for "Trust this device" option (means 2FA was successful)
                try:
                    trust_selectors = [
                        'button:has-text("Trust this device")',
                        'button:has-text("trust this device")',
                        'button:has-text("Trust Device")',
                        'div[role="button"]:has-text("Trust this device")'
                    ]
                    for selector in trust_selectors:
                        trust_elem = page.locator(selector).first
                        if await trust_elem.is_visible(timeout=1000):
                            print(f"✅ 'Trust this device' prompt detected (waited {i+1}s)")
                            print("   User successfully entered 2FA code")
                            return True
                except:
                    pass

                # Check for error messages
                try:
                    error_elem = page.locator('[data-testid="error-alert"]').first
                    if await error_elem.is_visible(timeout=1000):
                        error_text = await error_elem.text_content()
                        print(f"❌ 2FA error detected: {error_text}")
                        return False
                except:
                    pass

                # Wait 1 second before checking again
                await asyncio.sleep(1)

                # Show progress every 10 seconds
                if (i + 1) % 10 == 0:
                    print(f"   Still waiting... ({i+1}/60 seconds)")

            print("❌ Timeout waiting for manual 2FA entry")
            await self._save_debug_screenshot(page, "2fa_manual_timeout")
            return False

        except Exception as e:
            print(f"❌ Error waiting for manual 2FA: {e}")
            await self._save_debug_screenshot(page, "2fa_manual_error")
            return False

    async def _handle_trust_this_device(self, page) -> bool:
        """Handle 'Trust this device' option after successful 2FA.

        Instagram may show a prompt asking if you want to trust this device
        to avoid future 2FA requests.

        Returns:
            bool: True if handled or not needed, False if there's an error
        """
        print("🔍 Checking for 'Trust this device' option...")

        # Multiple selectors for different versions of this prompt
        trust_device_selectors = [
            'button:has-text("Trust this device")',
            'button:has-text("trust this device")',
            'button:has-text("Trust Device")',
            'button:has-text("trust device")',
            'button:has-text("Remember this device")',
            'button:has-text("remember this device")',
            'button:has-text("Save this device")',
            'button:has-text("save this device")',
            'div[role="button"]:has-text("Trust this device")',
            'div[role="button"]:has-text("Save this device")',
            'input[type="checkbox"][name="trust"]',
            'input[type="checkbox"][name="remember"]',
            'input[type="checkbox"][name="save"]',
            'input[type="checkbox"]'  # Generic checkbox as last resort
        ]

        for selector in trust_device_selectors:
            try:
                # Check if the element exists and is visible
                trust_element = page.locator(selector).first
                if await trust_element.is_visible(timeout=3000):
                    print(f"✅ Found 'Trust this device' element: {selector}")

                    # Click the element
                    await trust_element.click()
                    print(f"✅ Clicked 'Trust this device' option")
                    await page.wait_for_timeout(2000)

                    # Check if there's a confirmation button
                    confirm_selectors = [
                        'button:has-text("Continue")',
                        'button:has-text("continue")',
                        'button:has-text("OK")',
                        'button:has-text("ok")',
                        'button:has-text("Confirm")',
                        'button:has-text("confirm")',
                        'button[type="submit"]'
                    ]

                    for confirm_selector in confirm_selectors:
                        try:
                            confirm_button = page.locator(confirm_selector).first
                            if await confirm_button.is_visible(timeout=2000):
                                await confirm_button.click()
                                print(f"✅ Confirmed 'Trust this device' selection")
                                await page.wait_for_timeout(2000)
                                break
                        except:
                            continue

                    return True
            except:
                continue

        print("ℹ️  No 'Trust this device' option found or not needed")
        return True  # Return True even if not found - it's optional

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
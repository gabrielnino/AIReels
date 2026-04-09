"""
Browser Service for Instagram automation.

This module provides high-level browser management for Instagram automation,
including browser lifecycle, context management, and error recovery.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import asyncio
import os
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv

# Load Instagram configuration
load_dotenv('.env.instagram')


class BrowserType(Enum):
    """Supported browser types."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


@dataclass
class BrowserConfig:
    """Configuration for browser automation."""
    browser_type: BrowserType = BrowserType.CHROMIUM
    headless: bool = False
    slow_mo: int = 100  # milliseconds between actions
    timeout: int = 30000  # milliseconds
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    extra_args: list = field(default_factory=list)


class BrowserService:
    """High-level browser management service for Instagram automation."""

    def __init__(self, config: Optional[BrowserConfig] = None):
        """Initialize browser service.

        Args:
            config: Browser configuration. If None, uses environment variables.
        """
        self.config = config or self._create_config_from_env()
        self._browser = None
        self._context = None
        self._page = None
        self._is_initialized = False

    def _create_config_from_env(self) -> BrowserConfig:
        """Create configuration from environment variables."""
        return BrowserConfig(
            browser_type=BrowserType(
                os.getenv('BROWSER_TYPE', 'chromium').lower()
            ),
            headless=os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true',
            slow_mo=int(os.getenv('PLAYWRIGHT_SLOW_MO', '100')),
            timeout=int(os.getenv('PLAYWRIGHT_TIMEOUT', '30000')),
            viewport_width=int(os.getenv('BROWSER_VIEWPORT_WIDTH', '1920')),
            viewport_height=int(os.getenv('BROWSER_VIEWPORT_HEIGHT', '1080'))
        )

    async def initialize(self) -> None:
        """Initialize browser, context, and page."""
        if self._is_initialized:
            return

        print("🖥️  Initializing browser service...")

        from playwright.async_api import async_playwright

        try:
            # Launch playwright
            self._playwright = await async_playwright().start()

            # Launch browser
            browser_launcher = getattr(self._playwright, self.config.browser_type.value)
            self._browser = await browser_launcher.launch(
                headless=self.config.headless,
                slow_mo=self.config.slow_mo,
                args=self.config.extra_args
            )

            # Create browser context
            self._context = await self._browser.new_context(
                viewport={
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                },
                user_agent=self.config.user_agent
            )

            # Create page
            self._page = await self._context.new_page()
            self._page.set_default_timeout(self.config.timeout)

            self._is_initialized = True
            print(f"✅ Browser service initialized ({self.config.browser_type.value})")

        except Exception as e:
            print(f"❌ Browser initialization failed: {e}")
            await self.close()
            raise BrowserInitError(f"Failed to initialize browser: {e}")

    async def navigate_to_instagram(self) -> None:
        """Navigate to Instagram homepage."""
        if not self._is_initialized:
            await self.initialize()

        print("🌐 Navigating to Instagram...")
        await self._page.goto('https://www.instagram.com/')
        await self._page.wait_for_timeout(2000)

        # Handle cookies popup if present
        await self._handle_cookies_popup()

        print("✅ Navigated to Instagram")

    async def _handle_cookies_popup(self) -> None:
        """Handle cookies acceptance popup."""
        try:
            # Try different selectors for cookies popup
            selectors = [
                "button:has-text('Allow all cookies')",
                "button:has-text('Accept all')",
                "button:has-text('Accept')",
                "button[data-testid='cookie-banner-accept']"
            ]

            for selector in selectors:
                try:
                    button = self._page.locator(selector).first
                    if await button.is_visible(timeout=2000):
                        await button.click()
                        print("✅ Cookies accepted")
                        await self._page.wait_for_timeout(1000)
                        return
                except:
                    continue

        except Exception as e:
            print(f"⚠️  Could not handle cookies popup: {e}")

    async def take_screenshot(self, filename: str) -> str:
        """Take screenshot and save to file.

        Args:
            filename: Screenshot filename (without extension)

        Returns:
            Path to saved screenshot
        """
        if not self._is_initialized:
            raise BrowserNotInitializedError("Browser not initialized")

        screenshot_dir = Path("./logs/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / f"{filename}.png"
        await self._page.screenshot(path=str(screenshot_path))

        print(f"📸 Screenshot saved: {screenshot_path}")
        return str(screenshot_path)

    async def human_like_delay(self, min_ms: int = 500, max_ms: int = 2000) -> None:
        """Add human-like random delay between actions.

        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay = random.randint(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)

    async def type_like_human(self, selector: str, text: str) -> None:
        """Type text like a human with random delays between keystrokes.

        Args:
            selector: Element selector
            text: Text to type
        """
        element = self._page.locator(selector).first
        await element.click()
        await element.clear()

        for char in text:
            await element.type(char, delay=random.randint(50, 150))
            await self.human_like_delay(30, 100)

    async def click_like_human(self, selector: str) -> None:
        """Click element like a human with random movement.

        Args:
            selector: Element selector
        """
        element = self._page.locator(selector).first

        # Add random delay before clicking
        await self.human_like_delay(200, 800)

        # Click the element
        await element.click()

        # Add random delay after clicking
        await self.human_like_delay(200, 800)

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            True if element found, False otherwise
        """
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False

    async def is_element_visible(self, selector: str, timeout: int = 3000) -> bool:
        """Check if element is visible.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            True if element is visible, False otherwise
        """
        try:
            element = self._page.locator(selector).first
            return await element.is_visible(timeout=timeout)
        except:
            return False

    async def get_element_text(self, selector: str) -> Optional[str]:
        """Get text content of element.

        Args:
            selector: Element selector

        Returns:
            Text content or None if element not found
        """
        try:
            element = self._page.locator(selector).first
            return await element.text_content()
        except:
            return None

    async def reload_page(self) -> None:
        """Reload current page."""
        print("🔄 Reloading page...")
        await self._page.reload()
        await self._page.wait_for_timeout(2000)

    async def save_cookies(self, path: str = "./data/instagram_cookies.json") -> None:
        """Save browser cookies to file.

        Args:
            path: Path to save cookies
        """
        if not self._is_initialized:
            raise BrowserNotInitializedError("Browser not initialized")

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        cookies = await self._context.cookies()
        import json
        with open(path, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"💾 Cookies saved to: {path}")

    async def load_cookies(self, path: str = "./data/instagram_cookies.json") -> bool:
        """Load cookies from file.

        Args:
            path: Path to cookies file

        Returns:
            True if cookies loaded successfully, False otherwise
        """
        if not Path(path).exists():
            print(f"❌ Cookies file not found: {path}")
            return False

        try:
            import json
            with open(path, 'r') as f:
                cookies = json.load(f)

            await self._context.add_cookies(cookies)
            print(f"✅ Cookies loaded from: {path}")
            return True
        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            return False

    async def close(self) -> None:
        """Close browser and cleanup."""
        print("🧹 Cleaning up browser service...")

        try:
            if self._context:
                await self._context.close()
                self._context = None
        except:
            pass

        try:
            if self._browser:
                await self._browser.close()
                self._browser = None
        except:
            pass

        try:
            if hasattr(self, '_playwright'):
                await self._playwright.stop()
                delattr(self, '_playwright')
        except:
            pass

        self._page = None
        self._is_initialized = False
        print("✅ Browser service closed")

    @property
    def page(self):
        """Get current page."""
        if not self._is_initialized:
            raise BrowserNotInitializedError("Browser not initialized")
        return self._page

    @property
    def context(self):
        """Get current context."""
        if not self._is_initialized:
            raise BrowserNotInitializedError("Browser not initialized")
        return self._context

    @property
    def browser(self):
        """Get current browser."""
        if not self._is_initialized:
            raise BrowserNotInitializedError("Browser not initialized")
        return self._browser


# Exception classes
class BrowserError(Exception):
    """Base browser error."""
    pass

class BrowserInitError(BrowserError):
    """Browser initialization error."""
    pass

class BrowserNotInitializedError(BrowserError):
    """Browser not initialized error."""
    pass


# Example usage
async def example_usage():
    """Example usage of BrowserService."""
    print("BrowserService Example Usage")
    print("============================")

    # Create browser service
    config = BrowserConfig(
        browser_type=BrowserType.CHROMIUM,
        headless=False,
        slow_mo=100
    )

    service = BrowserService(config)

    try:
        # Initialize browser
        await service.initialize()

        # Navigate to Instagram
        await service.navigate_to_instagram()

        # Take screenshot
        await service.take_screenshot("instagram_homepage")

        # Human-like interaction
        await service.type_like_human('input[name="username"]', "test_user")

        # Save cookies
        await service.save_cookies()

        print("✅ Example completed successfully")

    except Exception as e:
        print(f"❌ Example failed: {e}")

    finally:
        # Always cleanup
        await service.close()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
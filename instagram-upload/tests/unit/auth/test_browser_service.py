"""
Unit tests for Browser Service.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.auth.browser_service import (
    BrowserType,
    BrowserConfig,
    BrowserService,
    BrowserError,
    BrowserInitError,
    BrowserNotInitializedError
)


class TestBrowserType:
    """Tests for BrowserType enum."""

    def test_browser_type_values(self):
        """Test browser type enum values."""
        assert BrowserType.CHROMIUM.value == "chromium"
        assert BrowserType.FIREFOX.value == "firefox"
        assert BrowserType.WEBKIT.value == "webkit"


class TestBrowserConfig:
    """Tests for BrowserConfig class."""

    def test_default_config(self):
        """Test default browser configuration."""
        config = BrowserConfig()

        assert config.browser_type == BrowserType.CHROMIUM
        assert config.headless == False
        assert config.slow_mo == 100
        assert config.timeout == 30000
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080
        assert "Mozilla" in config.user_agent
        assert config.extra_args == []

    def test_custom_config(self):
        """Test custom browser configuration."""
        config = BrowserConfig(
            browser_type=BrowserType.FIREFOX,
            headless=True,
            slow_mo=200,
            timeout=60000,
            viewport_width=1366,
            viewport_height=768,
            user_agent="Test Agent",
            extra_args=["--test-arg"]
        )

        assert config.browser_type == BrowserType.FIREFOX
        assert config.headless == True
        assert config.slow_mo == 200
        assert config.timeout == 60000
        assert config.viewport_width == 1366
        assert config.viewport_height == 768
        assert config.user_agent == "Test Agent"
        assert config.extra_args == ["--test-arg"]


class TestBrowserService:
    """Tests for BrowserService class."""

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = BrowserConfig(
            browser_type=BrowserType.FIREFOX,
            headless=True,
            slow_mo=200
        )

        service = BrowserService(config)
        assert service.config == config
        assert service._browser is None
        assert service._context is None
        assert service._page is None
        assert service._is_initialized == False

    def test_initialization_without_config(self):
        """Test initialization without config (uses environment)."""
        with patch.dict(os.environ, {
            'BROWSER_TYPE': 'firefox',
            'PLAYWRIGHT_HEADLESS': 'true',
            'PLAYWRIGHT_SLOW_MO': '200',
            'PLAYWRIGHT_TIMEOUT': '60000',
            'BROWSER_VIEWPORT_WIDTH': '1366',
            'BROWSER_VIEWPORT_HEIGHT': '768'
        }, clear=True):
            service = BrowserService()

            assert service.config.browser_type == BrowserType.FIREFOX
            assert service.config.headless == True
            assert service.config.slow_mo == 200
            assert service.config.timeout == 60000
            assert service.config.viewport_width == 1366
            assert service.config.viewport_height == 768

    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful browser initialization."""
        service = BrowserService()

        mock_playwright = Mock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        with patch('src.auth.browser_service.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_page.set_default_timeout = Mock()

            await service.initialize()

            assert service._is_initialized == True
            assert service._playwright == mock_playwright
            assert service._browser == mock_browser
            assert service._context == mock_context
            assert service._page == mock_page

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialization when already initialized."""
        service = BrowserService()
        service._is_initialized = True

        # Should return immediately without calling playwright
        with patch('src.auth.browser_service.async_playwright') as mock_async_playwright:
            await service.initialize()
            mock_async_playwright.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """Test browser initialization failure."""
        service = BrowserService()

        with patch('src.auth.browser_service.async_playwright') as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(side_effect=Exception("Test error"))

            with pytest.raises(BrowserInitError, match="Failed to initialize browser"):
                await service.initialize()

            # Should have called close on failure
            assert service._is_initialized == False

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing browser service."""
        service = BrowserService()

        # Mock initialized state
        service._is_initialized = True
        service._context = AsyncMock()
        service._browser = AsyncMock()
        service._playwright = Mock()
        service._playwright.stop = AsyncMock()

        await service.close()

        assert service._is_initialized == False
        assert service._context is None
        assert service._browser is None
        assert service._page is None

    def test_properties_not_initialized(self):
        """Test properties when browser not initialized."""
        service = BrowserService()

        with pytest.raises(BrowserNotInitializedError):
            _ = service.page

        with pytest.raises(BrowserNotInitializedError):
            _ = service.context

        with pytest.raises(BrowserNotInitializedError):
            _ = service.browser

    @pytest.mark.asyncio
    async def test_human_like_delay(self):
        """Test human-like delay."""
        service = BrowserService()

        with patch('asyncio.sleep') as mock_sleep:
            await service.human_like_delay(min_ms=1000, max_ms=2000)

            mock_sleep.assert_called_once()
            # Check that sleep was called with a value between 1.0 and 2.0 seconds
            sleep_arg = mock_sleep.call_args[0][0]
            assert 1.0 <= sleep_arg <= 2.0

    @pytest.mark.asyncio
    async def test_wait_for_element_found(self):
        """Test waiting for element that is found."""
        service = BrowserService()
        service._is_initialized = True
        service._page = AsyncMock()
        service._page.wait_for_selector = AsyncMock()

        result = await service.wait_for_element(".test-selector")
        assert result == True

    @pytest.mark.asyncio
    async def test_wait_for_element_not_found(self):
        """Test waiting for element that is not found."""
        service = BrowserService()
        service._is_initialized = True
        service._page = AsyncMock()
        service._page.wait_for_selector = AsyncMock(side_effect=Exception("Timeout"))

        result = await service.wait_for_element(".test-selector")
        assert result == False

    @pytest.mark.asyncio
    async def test_is_element_visible_true(self):
        """Test checking if element is visible (true case)."""
        service = BrowserService()
        service._is_initialized = True
        service._page = AsyncMock()

        mock_element = AsyncMock()
        mock_element.is_visible = AsyncMock(return_value=True)
        service._page.locator = Mock(return_value=mock_element)

        result = await service.is_element_visible(".test-selector")
        assert result == True

    @pytest.mark.asyncio
    async def test_is_element_visible_false(self):
        """Test checking if element is visible (false case)."""
        service = BrowserService()
        service._is_initialized = True
        service._page = AsyncMock()

        mock_element = AsyncMock()
        mock_element.is_visible = AsyncMock(side_effect=Exception("Not visible"))
        service._page.locator = Mock(return_value=mock_element)

        result = await service.is_element_visible(".test-selector")
        assert result == False

    @pytest.mark.asyncio
    async def test_get_element_text_found(self):
        """Test getting text from element that is found."""
        service = BrowserService()
        service._is_initialized = True
        service._page = AsyncMock()

        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="Test Text")
        service._page.locator = Mock(return_value=mock_element)

        result = await service.get_element_text(".test-selector")
        assert result == "Test Text"

    @pytest.mark.asyncio
    async def test_get_element_text_not_found(self):
        """Test getting text from element that is not found."""
        service = BrowserService()
        service._is_initialized = True
        service._page = AsyncMock()

        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(side_effect=Exception("Not found"))
        service._page.locator = Mock(return_value=mock_element)

        result = await service.get_element_text(".test-selector")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Integration tests for Authentication module.

Tests the interaction between BrowserService, LoginManager, and CookieManager.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from src.auth.browser_service import BrowserService, BrowserConfig
from src.auth.login_manager import InstagramLoginManager
from src.auth.cookie_manager import CookieManager, CookieRecord, SessionInfo


class TestAuthIntegration:
    """Integration tests for authentication components."""

    def test_browser_service_with_cookie_manager(self):
        """Test BrowserService integration with CookieManager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cookies_path = os.path.join(temp_dir, "cookies.json")
            session_path = os.path.join(temp_dir, "session.json")

            # Configure environment
            with patch.dict(os.environ, {
                'INSTAGRAM_COOKIES_PATH': cookies_path,
                'INSTAGRAM_SESSION_PATH': session_path
            }, clear=True):
                # Create cookie manager
                cookie_manager = CookieManager()

                # Create browser config
                config = BrowserConfig(
                    headless=True,  # Headless for testing
                    slow_mo=0  # No delay for tests
                )

                # Create browser service
                browser_service = BrowserService(config)

                assert browser_service.config == config
                assert cookie_manager.cookies_path == cookies_path
                assert cookie_manager.session_path == session_path

    @pytest.mark.asyncio
    async def test_login_manager_with_cookie_save_load(self):
        """Test LoginManager saving and loading cookies through CookieManager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cookies_path = os.path.join(temp_dir, "cookies.json")
            session_path = os.path.join(temp_dir, "session.json")

            # Configure environment for login manager
            with patch.dict(os.environ, {
                'INSTAGRAM_USERNAME': 'test_user',
                'INSTAGRAM_PASSWORD': 'test_password',
                'INSTAGRAM_ENABLE_2FA': 'false',
                'INSTAGRAM_COOKIES_PATH': cookies_path,
                'INSTAGRAM_SESSION_PATH': session_path,
                'PLAYWRIGHT_HEADLESS': 'true'
            }, clear=True):
                # Create managers
                login_manager = InstagramLoginManager()
                cookie_manager = CookieManager()

                # Mock successful login
                mock_context = AsyncMock()
                mock_context.cookies = AsyncMock(return_value=[
                    {
                        'name': 'sessionid',
                        'value': 'test_session_value',
                        'domain': '.instagram.com',
                        'path': '/',
                        'expires': datetime.now().timestamp() + 3600
                    }
                ])

                # Save cookies through cookie manager
                success = cookie_manager.save_cookies(
                    await mock_context.cookies(),
                    login_manager.username
                )

                assert success == True
                assert os.path.exists(cookies_path)
                assert os.path.exists(session_path)

                # Load cookies back
                loaded_cookies, session_info = cookie_manager.load_cookies()

                assert len(loaded_cookies) == 1
                assert loaded_cookies[0]['name'] == 'sessionid'
                assert loaded_cookies[0]['value'] == 'test_session_value'
                assert session_info is not None
                assert session_info.username == 'test_user'

    @pytest.mark.asyncio
    async def test_complete_auth_flow_mocked(self):
        """Test complete authentication flow with all components (mocked)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cookies_path = os.path.join(temp_dir, "cookies.json")
            session_path = os.path.join(temp_dir, "session.json")

            # Configure environment
            with patch.dict(os.environ, {
                'INSTAGRAM_USERNAME': 'test_user',
                'INSTAGRAM_PASSWORD': 'test_password',
                'INSTAGRAM_ENABLE_2FA': 'false',
                'INSTAGRAM_COOKIES_PATH': cookies_path,
                'INSTAGRAM_SESSION_PATH': session_path,
                'PLAYWRIGHT_HEADLESS': 'true',
                'PLAYWRIGHT_SLOW_MO': '0'
            }, clear=True):
                # Create all components
                browser_service = BrowserService()
                login_manager = InstagramLoginManager()
                cookie_manager = CookieManager()

                # Mock browser initialization
                mock_playwright = Mock()
                mock_browser = AsyncMock()
                mock_context = AsyncMock()
                mock_page = AsyncMock()

                with patch('playwright.async_api.async_playwright') as mock_async_playwright:
                    mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
                    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
                    mock_browser.new_context = AsyncMock(return_value=mock_context)
                    mock_context.new_page = AsyncMock(return_value=mock_page)
                    mock_page.set_default_timeout = Mock()

                    # Initialize browser
                    await browser_service.initialize()
                    assert browser_service._is_initialized == True

                # Mock successful login
                mock_page.goto = AsyncMock()
                mock_page.wait_for_timeout = AsyncMock()
                mock_page.fill = AsyncMock()
                mock_page.click = AsyncMock()
                mock_page.wait_for_selector = AsyncMock()

                # Mock cookie saving
                mock_context.cookies = AsyncMock(return_value=[
                    {
                        'name': 'sessionid',
                        'value': 'test_session',
                        'domain': '.instagram.com',
                        'path': '/'
                    }
                ])

                # Test session validity
                assert not cookie_manager.has_valid_session()

                # Simulate successful cookie save
                success = cookie_manager.save_cookies(
                    await mock_context.cookies(),
                    login_manager.username
                )
                assert success == True

                # Now should have valid session
                assert cookie_manager.has_valid_session()

                # Get session username
                username = cookie_manager.get_session_username()
                assert username == 'test_user'

    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Test ConfigurationError propagation
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                InstagramLoginManager()

            # Should raise ConfigurationError
            assert "INSTAGRAM_USERNAME not configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_session_expiration_flow(self):
        """Test session expiration and renewal flow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_path = os.path.join(temp_dir, "session.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_SESSION_PATH': session_path,
                'INSTAGRAM_SESSION_TIMEOUT': '1'  # 1 second timeout for test
            }, clear=True):
                cookie_manager = CookieManager()

                # Create session that will expire immediately
                old_time = datetime.now() - timedelta(seconds=10)
                session = SessionInfo(
                    username="test_user",
                    created_at=old_time,
                    last_used=old_time,
                    expires_at=old_time + timedelta(seconds=1)  # Already expired
                )
                cookie_manager.save_session_info(session)

                # Session should be considered expired
                assert not cookie_manager.has_valid_session()

                # Session should be marked invalid
                loaded_session = cookie_manager.load_session_info()
                assert loaded_session is not None
                assert loaded_session.is_valid == False

    def test_cookie_record_to_browser_format(self):
        """Test CookieRecord conversion to browser-compatible format."""
        # Create CookieRecord
        expires = datetime.now().timestamp() + 3600
        cookie_record = CookieRecord(
            name="test_cookie",
            value="test_value",
            domain=".instagram.com",
            path="/",
            expires=expires,
            http_only=True,
            secure=True,
            same_site="Lax"
        )

        # Convert to browser format
        browser_cookie = cookie_record.to_dict()

        # Verify browser-compatible format
        assert browser_cookie["name"] == "test_cookie"
        assert browser_cookie["value"] == "test_value"
        assert browser_cookie["domain"] == ".instagram.com"
        assert browser_cookie["path"] == "/"
        assert browser_cookie["expires"] == expires
        assert browser_cookie["httpOnly"] == True  # Note: capital O
        assert browser_cookie["secure"] == True
        assert browser_cookie["sameSite"] == "Lax"

        # Convert back from browser format
        restored_record = CookieRecord.from_dict(browser_cookie)

        assert restored_record.name == cookie_record.name
        assert restored_record.value == cookie_record.value
        assert restored_record.domain == cookie_record.domain
        assert restored_record.path == cookie_record.path
        assert restored_record.expires == cookie_record.expires
        assert restored_record.http_only == cookie_record.http_only
        assert restored_record.secure == cookie_record.secure
        assert restored_record.same_site == cookie_record.same_site

    @pytest.mark.asyncio
    async def test_utility_functions_integration(self):
        """Test utility functions that bridge components."""
        from src.auth.cookie_manager import save_cookies_from_context, load_cookies_to_context

        # Mock context
        mock_context = AsyncMock()
        mock_context.cookies = AsyncMock(return_value=[
            {"name": "sessionid", "value": "test"}
        ])

        # Mock CookieManager
        with patch('src.auth.cookie_manager.CookieManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager

            # Test save_cookies_from_context
            mock_manager.save_cookies = Mock(return_value=True)
            success = await save_cookies_from_context(mock_context, "test_user")
            assert success == True

            # Test load_cookies_to_context
            mock_manager.load_cookies = Mock(return_value=([
                {"name": "sessionid", "value": "test"}
            ], Mock()))
            mock_context.add_cookies = AsyncMock()

            success, session_info = await load_cookies_to_context(mock_context)
            assert success == True
            assert session_info is not None
            mock_context.add_cookies.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
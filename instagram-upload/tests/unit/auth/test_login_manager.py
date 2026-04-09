"""
Unit tests for Instagram Login Manager.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from src.auth.login_manager import (
    InstagramLoginManager,
    LoginCredentials,
    TwoFactorCode,
    ConfigurationError,
    AuthenticationError,
    TwoFactorRequiredError,
    TwoFactorInputError
)


class TestLoginCredentials:
    """Tests for LoginCredentials class."""

    def test_valid_credentials(self):
        """Test valid credentials initialization."""
        credentials = LoginCredentials(
            username="test_user",
            password="test_password",
            enable_2fa=True
        )
        assert credentials.username == "test_user"
        assert credentials.password == "test_password"
        assert credentials.enable_2fa == True

    def test_empty_username(self):
        """Test validation with empty username."""
        with pytest.raises(ValueError, match="Username and password must be provided"):
            LoginCredentials(username="", password="password")

    def test_empty_password(self):
        """Test validation with empty password."""
        with pytest.raises(ValueError, match="Username and password must be provided"):
            LoginCredentials(username="user", password="")

    def test_short_username(self):
        """Test validation with short username."""
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            LoginCredentials(username="ab", password="password")

    def test_short_password(self):
        """Test validation with short password."""
        with pytest.raises(ValueError, match="Password must be at least 6 characters"):
            LoginCredentials(username="user", password="12345")


class TestTwoFactorCode:
    """Tests for TwoFactorCode class."""

    def test_valid_code(self):
        """Test valid 2FA code."""
        timestamp = datetime.now()
        code = TwoFactorCode(code="123456", timestamp=timestamp)
        assert code.code == "123456"
        assert code.timestamp == timestamp

    def test_wrong_length(self):
        """Test validation with wrong length code."""
        timestamp = datetime.now()
        with pytest.raises(ValueError, match="2FA code must be exactly 6 digits"):
            TwoFactorCode(code="12345", timestamp=timestamp)

        with pytest.raises(ValueError, match="2FA code must be exactly 6 digits"):
            TwoFactorCode(code="1234567", timestamp=timestamp)

    def test_non_digit_code(self):
        """Test validation with non-digit code."""
        timestamp = datetime.now()
        with pytest.raises(ValueError, match="2FA code must contain only digits"):
            TwoFactorCode(code="12345a", timestamp=timestamp)

    def test_expired_code(self):
        """Test validation with expired code."""
        timestamp = datetime.now() - timedelta(seconds=61)
        with pytest.raises(ValueError, match="2FA code has expired"):
            TwoFactorCode(code="123456", timestamp=timestamp)


class TestInstagramLoginManager:
    """Tests for InstagramLoginManager class."""

    def test_initialization_with_missing_env(self):
        """Test initialization with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError, match="INSTAGRAM_USERNAME not configured"):
                InstagramLoginManager()

    def test_initialization_with_default_values(self):
        """Test initialization with default placeholder values."""
        with patch.dict(os.environ, {
            'INSTAGRAM_USERNAME': 'your_instagram_username_here',
            'INSTAGRAM_PASSWORD': 'your_instagram_password_here'
        }, clear=True):
            with pytest.raises(ConfigurationError, match="INSTAGRAM_USERNAME not configured"):
                InstagramLoginManager()

    def test_initialization_with_valid_env(self):
        """Test initialization with valid environment variables."""
        with patch.dict(os.environ, {
            'INSTAGRAM_USERNAME': 'test_user',
            'INSTAGRAM_PASSWORD': 'test_password',
            'INSTAGRAM_ENABLE_2FA': 'true',
            'INSTAGRAM_COOKIES_PATH': './test_cookies.json',
            'PLAYWRIGHT_HEADLESS': 'false',
            'PLAYWRIGHT_SLOW_MO': '100',
            'PLAYWRIGHT_TIMEOUT': '30000'
        }, clear=True):
            manager = InstagramLoginManager()

            assert manager.username == 'test_user'
            assert manager.password == 'test_password'
            assert manager.enable_2fa == True
            assert manager.cookies_path == './test_cookies.json'
            assert manager.headless == False
            assert manager.slow_mo == 100
            assert manager.timeout == 30000

            # Check credentials object
            assert manager.credentials.username == 'active_user'
            assert manager.credentials.password == 'actual_password'
            assert manager.credentials.enable_2fa == True

    @pytest.mark.asyncio
    async def test_get_two_factor_code_interactive(self):
        """Test getting 2FA code in interactive mode."""
        manager = InstagramLoginManager()

        # Mock stdin.isatty to return True (interactive)
        with patch('sys.stdin.isatty', return_value=True):
            # Mock input to return test code
            with patch('builtins.input', return_value='123456'):
                code = manager._get_two_factor_code_from_user()
                assert code == '123456'

    @pytest.mark.asyncio
    async def test_get_two_factor_code_non_interactive(self):
        """Test getting 2FA code in non-interactive mode."""
        manager = InstagramLoginManager()

        # Mock stdin.isatty to return False (non-interactive)
        with patch('sys.stdin.isatty', return_value=False):
            # Mock environment variable
            with patch.dict(os.environ, {'INSTAGRAM_2FA_CODE': '123456'}):
                code = manager._get_two_factor_code_from_user()
                assert code == '123456'

    @pytest.mark.asyncio
    async def test_get_two_factor_code_non_interactive_missing(self):
        """Test getting 2FA code in non-interactive mode without env var."""
        manager = InstagramLoginManager()

        # Mock stdin.isatty to return False (non-interactive)
        with patch('sys.stdin.isatty', return_value=False):
            # Clear environment variable
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(TwoFactorInputError):
                    manager._get_two_factor_code_from_user()

    @pytest.mark.asyncio
    async def test_save_session_cookies(self):
        """Test saving session cookies."""
        manager = InstagramLoginManager()

        # Mock context and cookies
        mock_context = AsyncMock()
        mock_context.cookies = AsyncMock(return_value=[
            {'name': 'sessionid', 'value': 'test_session'}
        ])

        # Mock Path and open
        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open') as mock_open:
                mock_file = Mock()
                mock_open.return_value = mock_file

                await manager._save_session_cookies(mock_context)

                # Verify file was opened
                mock_open.assert_called_once_with(manager.cookies_path, 'w')

                # Verify json.dump was called
                # (we can't easily mock json.dump, but we can verify the file write)

    @pytest.mark.asyncio
    async def test_login_with_cookies_success(self):
        """Test successful login with cookies."""
        manager = InstagramLoginManager()

        # Mock Path.exists to return True
        with patch('pathlib.Path.exists', return_value=True):
            # Mock async_playwright and browser interactions
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            with patch('src.auth.login_manager.async_playwright') as mock_playwright:
                mock_p = AsyncMock()
                mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)

                mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_browser.new_context = AsyncMock(return_value=mock_context)
                mock_context.new_page = AsyncMock(return_value=mock_page)

                # Mock cookie loading
                with patch('builtins.open'):
                    with patch('json.load', return_value=[{'name': 'cookie', 'value': 'test'}]):
                        mock_context.add_cookies = AsyncMock()

                # Mock page interactions
                mock_page.goto = AsyncMock()
                mock_page.wait_for_timeout = AsyncMock()

                # Mock successful login detection
                mock_page.wait_for_selector = AsyncMock()

                # Run test
                result = await manager.login_with_cookies()

                assert result == True

    @pytest.mark.asyncio
    async def test_login_with_cookies_no_file(self):
        """Test login with cookies when file doesn't exist."""
        manager = InstagramLoginManager()

        # Mock Path.exists to return False
        with patch('pathlib.Path.exists', return_value=False):
            result = await manager.login_with_cookies()

            assert result == False

    @pytest.mark.asyncio
    async def test_login_with_cookies_expired(self):
        """Test login with expired cookies."""
        manager = InstagramLoginManager()

        # Mock Path.exists to return True
        with patch('pathlib.Path.exists', return_value=True):
            # Mock async_playwright and browser interactions
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            with patch('src.auth.login_manager.async_playwright') as mock_playwright:
                mock_p = AsyncMock()
                mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)

                mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_browser.new_context = AsyncMock(return_value=mock_context)
                mock_context.new_page = AsyncMock(return_value=mock_page)

                # Mock cookie loading
                with patch('builtins.open'):
                    with patch('json.load', return_value=[{'name': 'cookie', 'value': 'test'}]):
                        mock_context.add_cookies = AsyncMock()

                # Mock page interactions
                mock_page.goto = AsyncMock()
                mock_page.wait_for_timeout = AsyncMock()

                # Mock failed login detection (selector not found)
                mock_page.wait_for_selector = AsyncMock(side_effect=Exception("Selector not found"))

                # Run test
                result = await manager.login_with_cookies()

                assert result == False


# Test fixtures
@pytest.fixture
def mock_credentials():
    """Fixture for mock credentials."""
    return LoginCredentials(
        username="test_user",
        password="test_password",
        enable_2fa=True
    )

@pytest.fixture
def mock_login_manager():
    """Fixture for mock login manager."""
    with patch.dict(os.environ, {
        'INSTAGRAM_USERNAME': 'test_user',
        'INSTAGRAM_PASSWORD': 'test_password',
        'INSTAGRAM_ENABLE_2FA': 'true',
        'INSTAGRAM_COOKIES_PATH': './test_cookies.json',
        'PLAYWRIGHT_HEADLESS': 'false'
    }, clear=True):
        return InstagramLoginManager()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
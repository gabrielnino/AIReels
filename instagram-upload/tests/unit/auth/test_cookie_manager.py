"""
Unit tests for Cookie Manager.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from src.auth.cookie_manager import (
    CookieRecord,
    SessionInfo,
    CookieManager,
    save_cookies_from_context,
    load_cookies_to_context
)


class TestCookieRecord:
    """Tests for CookieRecord class."""

    def test_valid_cookie_record(self):
        """Test valid cookie record initialization."""
        expires = datetime.now().timestamp() + 3600
        record = CookieRecord(
            name="sessionid",
            value="test_value",
            domain=".instagram.com",
            path="/",
            expires=expires,
            http_only=True,
            secure=True,
            same_site="Lax"
        )

        assert record.name == "sessionid"
        assert record.value == "test_value"
        assert record.domain == ".instagram.com"
        assert record.path == "/"
        assert record.expires == expires
        assert record.http_only == True
        assert record.secure == True
        assert record.same_site == "Lax"

    def test_cookie_not_expired(self):
        """Test cookie expiration check when not expired."""
        expires = datetime.now().timestamp() + 100  # 100 seconds in future
        record = CookieRecord(
            name="test",
            value="value",
            domain=".test.com",
            path="/",
            expires=expires
        )
        assert not record.is_expired()

    def test_cookie_expired(self):
        """Test cookie expiration check when expired."""
        expires = datetime.now().timestamp() - 100  # 100 seconds in past
        record = CookieRecord(
            name="test",
            value="value",
            domain=".test.com",
            path="/",
            expires=expires
        )
        assert record.is_expired()

    def test_cookie_no_expiry(self):
        """Test cookie with no expiration date."""
        record = CookieRecord(
            name="test",
            value="value",
            domain=".test.com",
            path="/",
            expires=None
        )
        assert not record.is_expired()

    def test_to_dict(self):
        """Test conversion to dictionary."""
        expires = datetime.now().timestamp() + 3600
        record = CookieRecord(
            name="sessionid",
            value="test_value",
            domain=".instagram.com",
            path="/",
            expires=expires,
            http_only=True,
            secure=True,
            same_site="Lax"
        )

        cookie_dict = record.to_dict()
        assert cookie_dict["name"] == "sessionid"
        assert cookie_dict["value"] == "test_value"
        assert cookie_dict["domain"] == ".instagram.com"
        assert cookie_dict["path"] == "/"
        assert cookie_dict["expires"] == expires
        assert cookie_dict["httpOnly"] == True
        assert cookie_dict["secure"] == True
        assert cookie_dict["sameSite"] == "Lax"

    def test_from_dict(self):
        """Test creation from dictionary."""
        expires = datetime.now().timestamp() + 3600
        cookie_dict = {
            "name": "sessionid",
            "value": "test_value",
            "domain": ".instagram.com",
            "path": "/",
            "expires": expires,
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        }

        record = CookieRecord.from_dict(cookie_dict)
        assert record.name == "sessionid"
        assert record.value == "test_value"
        assert record.domain == ".instagram.com"
        assert record.path == "/"
        assert record.expires == expires
        assert record.http_only == True
        assert record.secure == True
        assert record.same_site == "Lax"


class TestSessionInfo:
    """Tests for SessionInfo class."""

    def test_valid_session_info(self):
        """Test valid session info initialization."""
        now = datetime.now()
        expires = now + timedelta(hours=1)

        session = SessionInfo(
            username="test_user",
            created_at=now,
            last_used=now,
            is_valid=True,
            expires_at=expires,
            metadata={"key": "value"}
        )

        assert session.username == "test_user"
        assert session.created_at == now
        assert session.last_used == now
        assert session.is_valid == True
        assert session.expires_at == expires
        assert session.metadata == {"key": "value"}

    def test_update_usage(self):
        """Test updating last used timestamp."""
        old_time = datetime(2026, 4, 8, 12, 0, 0)
        session = SessionInfo(
            username="test_user",
            created_at=old_time,
            last_used=old_time,
            expires_at=old_time + timedelta(hours=1)
        )

        # Mock datetime.now to return a specific time
        new_time = datetime(2026, 4, 8, 12, 30, 0)
        with patch('src.auth.cookie_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = new_time
            session.update_usage()

        assert session.last_used == new_time

    def test_mark_invalid(self):
        """Test marking session as invalid."""
        session = SessionInfo(
            username="test_user",
            created_at=datetime.now(),
            last_used=datetime.now(),
            is_valid=True
        )

        session.mark_invalid()
        assert session.is_valid == False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        now = datetime.now()
        expires = now + timedelta(hours=1)

        session = SessionInfo(
            username="test_user",
            created_at=now,
            last_used=now,
            is_valid=True,
            expires_at=expires,
            metadata={"key": "value"}
        )

        session_dict = session.to_dict()
        assert session_dict["username"] == "test_user"
        assert session_dict["created_at"] == now.isoformat()
        assert session_dict["last_used"] == now.isoformat()
        assert session_dict["is_valid"] == True
        assert session_dict["expires_at"] == expires.isoformat()
        assert session_dict["metadata"] == {"key": "value"}

    def test_from_dict(self):
        """Test creation from dictionary."""
        now = datetime.now()
        expires = now + timedelta(hours=1)

        session_dict = {
            "username": "test_user",
            "created_at": now.isoformat(),
            "last_used": now.isoformat(),
            "is_valid": True,
            "expires_at": expires.isoformat(),
            "metadata": {"key": "value"}
        }

        session = SessionInfo.from_dict(session_dict)
        assert session.username == "test_user"
        assert session.created_at == now
        assert session.last_used == now
        assert session.is_valid == True
        assert session.expires_at == expires
        assert session.metadata == {"key": "value"}


class TestCookieManager:
    """Tests for CookieManager class."""

    def test_initialization(self):
        """Test cookie manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cookies_path = os.path.join(temp_dir, "cookies.json")
            session_path = os.path.join(temp_dir, "session.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_COOKIES_PATH': cookies_path,
                'INSTAGRAM_SESSION_PATH': session_path,
                'INSTAGRAM_ENCRYPTION_KEY': 'test_key_32_bytes_long_test_key_32'
            }, clear=True):
                manager = CookieManager()

                assert manager.cookies_path == cookies_path
                assert manager.session_path == session_path
                assert manager.encryption_key == 'test_key_32_bytes_long_test_key_32'
                assert manager.session_timeout == 3600  # default

    def test_save_cookies_no_encryption(self):
        """Test saving cookies without encryption."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cookies_path = os.path.join(temp_dir, "cookies.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_COOKIES_PATH': cookies_path,
                'INSTAGRAM_SESSION_PATH': os.path.join(temp_dir, "session.json")
            }, clear=True):
                manager = CookieManager()

                example_cookies = [
                    {"name": "sessionid", "value": "test", "domain": ".instagram.com", "path": "/"}
                ]

                success = manager.save_cookies(example_cookies, "test_user")
                assert success == True

                # Verify file was created
                assert os.path.exists(cookies_path)
                assert os.path.exists(os.path.join(temp_dir, "session.json"))

    def test_load_cookies_no_file(self):
        """Test loading cookies when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cookies_path = os.path.join(temp_dir, "nonexistent.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_COOKIES_PATH': cookies_path
            }, clear=True):
                manager = CookieManager()

                cookies, session_info = manager.load_cookies()
                assert cookies == []
                assert session_info is None

    def test_has_valid_session_no_session(self):
        """Test checking session validity when no session exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_path = os.path.join(temp_dir, "session.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_SESSION_PATH': session_path
            }, clear=True):
                manager = CookieManager()

                assert manager.has_valid_session() == False

    def test_invalidate_session(self):
        """Test invalidating a session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_path = os.path.join(temp_dir, "session.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_SESSION_PATH': session_path
            }, clear=True):
                manager = CookieManager()

                # Create a session first
                now = datetime.now()
                expires = now + timedelta(hours=1)
                session = SessionInfo(
                    username="test_user",
                    created_at=now,
                    last_used=now,
                    is_valid=True,
                    expires_at=expires
                )
                manager.save_session_info(session)

                # Invalidate it
                success = manager.invalidate_session()
                assert success == True

                # Load and check
                loaded_session = manager.load_session_info()
                assert loaded_session is not None
                assert loaded_session.is_valid == False

    def test_clear_all(self):
        """Test clearing all data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cookies_path = os.path.join(temp_dir, "cookies.json")
            session_path = os.path.join(temp_dir, "session.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_COOKIES_PATH': cookies_path,
                'INSTAGRAM_SESSION_PATH': session_path
            }, clear=True):
                manager = CookieManager()

                # Create files
                with open(cookies_path, 'w') as f:
                    f.write('test')
                with open(session_path, 'w') as f:
                    f.write('test')

                # Clear all
                success = manager.clear_all()
                assert success == True
                assert not os.path.exists(cookies_path)
                assert not os.path.exists(session_path)

    def test_get_session_username(self):
        """Test getting username from session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_path = os.path.join(temp_dir, "session.json")

            with patch.dict(os.environ, {
                'INSTAGRAM_SESSION_PATH': session_path
            }, clear=True):
                manager = CookieManager()

                # Create a session
                session = SessionInfo(
                    username="test_user",
                    created_at=datetime.now(),
                    last_used=datetime.now()
                )
                manager.save_session_info(session)

                username = manager.get_session_username()
                assert username == "test_user"


@pytest.mark.asyncio
async def test_save_cookies_from_context():
    """Test saving cookies from browser context."""
    mock_context = Mock()
    mock_context.cookies = Mock(return_value=[
        {"name": "sessionid", "value": "test", "domain": ".instagram.com"}
    ])

    with patch('src.auth.cookie_manager.CookieManager') as mock_manager_class:
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.save_cookies = Mock(return_value=True)

        success = await save_cookies_from_context(mock_context, "test_user")
        assert success == True
        mock_manager.save_cookies.assert_called_once()


@pytest.mark.asyncio
async def test_load_cookies_to_context():
    """Test loading cookies to browser context."""
    mock_context = Mock()
    mock_context.add_cookies = Mock()

    with patch('src.auth.cookie_manager.CookieManager') as mock_manager_class:
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.load_cookies = Mock(return_value=([
            {"name": "sessionid", "value": "test"}
        ], Mock()))

        success, session_info = await load_cookies_to_context(mock_context)
        assert success == True
        assert session_info is not None
        mock_context.add_cookies.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
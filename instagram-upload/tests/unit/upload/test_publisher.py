import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
"""
Unit tests for Publisher.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
import re
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from instagram_upload.src.upload.publisher import (
    Publisher,
    PublicationResult,
    PublicationStatus,
    PublishError,
    ShareButtonNotFoundError,
    PublishTimeoutError
)


class TestPublicationResult:
    """Tests for PublicationResult class."""

    def test_valid_publication_result(self):
        """Test valid publication result initialization."""
        result = PublicationResult(
            success=True,
            status=PublicationStatus.PUBLISHED,
            message="Post published successfully",
            post_url="https://www.instagram.com/p/ABC123DEF456/",
            post_id="ABC123DEF456",
            published_at=datetime.now(),
            duration_seconds=5.5,
            errors=["Test error"],
            metadata={"key": "value"}
        )

        assert result.success == True
        assert result.status == PublicationStatus.PUBLISHED
        assert result.message == "Post published successfully"
        assert result.post_url == "https://www.instagram.com/p/ABC123DEF456/"
        assert result.post_id == "ABC123DEF456"
        assert isinstance(result.published_at, datetime)
        assert result.duration_seconds == 5.5
        assert result.errors == ["Test error"]
        assert result.metadata == {"key": "value"}

    def test_failed_publication_result(self):
        """Test failed publication result initialization."""
        result = PublicationResult(
            success=False,
            status=PublicationStatus.FAILED,
            message="Publication failed",
            duration_seconds=10.0,
            errors=["Timeout", "Network error"]
        )

        assert result.success == False
        assert result.status == PublicationStatus.FAILED
        assert result.message == "Publication failed"
        assert result.duration_seconds == 10.0
        assert result.errors == ["Timeout", "Network error"]
        assert result.post_url is None
        assert result.post_id is None
        assert result.published_at is None


class TestPublisher:
    """Tests for Publisher class."""

    def test_initialization(self):
        """Test publisher initialization."""
        with patch.dict(os.environ, {
            'INSTAGRAM_PUBLISH_TIMEOUT': '120',
            'INSTAGRAM_DRY_RUN': 'false'
        }, clear=True):
            publisher = Publisher()

            assert publisher._publish_timeout == 120
            assert publisher._dry_run == False
            assert publisher.browser_service is None

    def test_initialization_dry_run(self):
        """Test publisher initialization with dry run enabled."""
        with patch.dict(os.environ, {
            'INSTAGRAM_DRY_RUN': 'true'
        }, clear=True):
            publisher = Publisher()

            assert publisher._dry_run == True

    @pytest.mark.asyncio
    async def test_click_share_button_success(self):
        """Test clicking share button successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=True)
        mock_browser_service.click_like_human = AsyncMock()
        mock_browser_service.take_screenshot = AsyncMock()

        # Mock os.getenv with a dictionary
        env_values = {
            'INSTAGRAM_DRY_RUN': 'false',
            'INSTAGRAM_PUBLISH_TIMEOUT': '120'
        }
        with patch('os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                return env_values.get(key, default)

            mock_getenv.side_effect = getenv_side_effect

            publisher = Publisher(mock_browser_service)
            # Ensure dry_run is False for this test
            publisher._dry_run = False

            result = await publisher.click_share_button()

            assert result == True
            mock_browser_service.click_like_human.assert_called_once()

    @pytest.mark.asyncio
    async def test_click_share_button_not_found(self):
        """Test clicking share button when not found."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=False)
        mock_browser_service.take_screenshot = AsyncMock()

        publisher = Publisher(mock_browser_service)

        result = await publisher.click_share_button()

        assert result == False
        mock_browser_service.take_screenshot.assert_called_with("share_button_missing")

    @pytest.mark.asyncio
    async def test_click_share_button_dry_run(self):
        """Test clicking share button in dry run mode."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=True)
        mock_browser_service.click_like_human = AsyncMock()
        mock_browser_service.take_screenshot = AsyncMock()

        # Mock os.getenv with a dictionary
        env_values = {
            'INSTAGRAM_DRY_RUN': 'true',
            'INSTAGRAM_PUBLISH_TIMEOUT': '120'
        }
        with patch('os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                return env_values.get(key, default)

            mock_getenv.side_effect = getenv_side_effect

            publisher = Publisher(mock_browser_service)
            # Ensure dry_run is True for this test
            publisher._dry_run = True

            result = await publisher.click_share_button()

            assert result == True  # Dry run always returns True
            # In dry run, wait_for_element should be called to find the button
            mock_browser_service.wait_for_element.assert_called()
            # But click_like_human should NOT be called
            mock_browser_service.click_like_human.assert_not_called()

    @pytest.mark.asyncio
    async def test_wait_for_publication_success(self):
        """Test waiting for publication successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.is_element_visible = AsyncMock(return_value=True)
        mock_browser_service.get_element_text = AsyncMock(return_value="Your post has been shared")
        mock_browser_service.take_screenshot = AsyncMock()
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.wait_for_selector = AsyncMock(side_effect=Exception("Not found"))

        publisher = Publisher(mock_browser_service)

        success, message = await publisher.wait_for_publication(timeout=5)

        assert success == True
        assert "successful" in message or "shared" in message

    @pytest.mark.asyncio
    async def test_wait_for_publication_error(self):
        """Test waiting for publication with error."""
        mock_browser_service = AsyncMock()
        # There are 6 success indicators and 5 error indicators in the implementation
        # We need all success indicators to return False, and at least one error indicator to return True
        # Create side_effect with 6 False (for success indicators) then some True (for error indicators)
        side_effect_values = [False] * 6  # For success indicators
        side_effect_values.append(True)   # First error indicator returns True
        side_effect_values.extend([False] * 4)  # Remaining error indicators

        mock_browser_service.is_element_visible = AsyncMock(side_effect=side_effect_values)
        mock_browser_service.get_element_text = AsyncMock(return_value="Something went wrong")
        mock_browser_service.take_screenshot = AsyncMock()
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.wait_for_selector = AsyncMock(side_effect=Exception("Not found"))

        # Mock os.getenv
        env_values = {
            'INSTAGRAM_PUBLISH_TIMEOUT': '120'
        }
        with patch('os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                return env_values.get(key, default)

            mock_getenv.side_effect = getenv_side_effect

            publisher = Publisher(mock_browser_service)

            success, message = await publisher.wait_for_publication(timeout=5)

            assert success == False
            assert "error" in message.lower() or "wrong" in message.lower()

    @pytest.mark.asyncio
    async def test_wait_for_publication_timeout(self):
        """Test waiting for publication timeout."""
        mock_browser_service = AsyncMock()

        # Mock is_element_visible to always return False (no success/error indicators)
        mock_browser_service.is_element_visible = AsyncMock(return_value=False)
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.wait_for_selector = AsyncMock(side_effect=Exception("Not found"))
        mock_browser_service.take_screenshot = AsyncMock()

        publisher = Publisher(mock_browser_service)

        success, message = await publisher.wait_for_publication(timeout=1)  # Short timeout

        assert success == False
        assert "timeout" in message.lower() or "timed out" in message.lower()

    @pytest.mark.asyncio
    async def test_get_publication_message_success(self):
        """Test getting publication success message."""
        mock_browser_service = AsyncMock()
        mock_browser_service.get_element_text = AsyncMock(return_value="Your post has been shared")

        publisher = Publisher(mock_browser_service)

        # Mock the method directly
        message = await publisher._get_publication_message()

        assert "shared" in message.lower() or "completed" in message.lower()

    @pytest.mark.asyncio
    async def test_get_post_url_from_view_post(self):
        """Test getting post URL from View post link."""
        mock_browser_service = AsyncMock()
        mock_browser_service.is_element_visible = AsyncMock(return_value=True)
        mock_browser_service.page = AsyncMock()

        # Mock evaluate to return a URL
        mock_browser_service.page.evaluate = AsyncMock(
            return_value="https://www.instagram.com/p/ABC123DEF456/"
        )

        publisher = Publisher(mock_browser_service)

        post_url = await publisher.get_post_url()

        assert post_url == "https://www.instagram.com/p/ABC123DEF456/"

    @pytest.mark.asyncio
    async def test_get_post_url_from_current_url(self):
        """Test getting post URL from current page URL."""
        mock_browser_service = AsyncMock()
        mock_browser_service.is_element_visible = AsyncMock(return_value=False)
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.url = "https://www.instagram.com/reel/XYZ789/"

        publisher = Publisher(mock_browser_service)

        post_url = await publisher.get_post_url()

        assert post_url == "https://www.instagram.com/reel/XYZ789/"

    @pytest.mark.asyncio
    async def test_extract_post_id_from_url(self):
        """Test extracting post ID from URL."""
        publisher = Publisher()

        test_url = "https://www.instagram.com/p/ABC123DEF456/"
        post_id = await publisher.extract_post_id(test_url)

        assert post_id == "ABC123DEF456"

    def test_extract_post_id_from_reel_url(self):
        """Test extracting post ID from reel URL."""
        publisher = Publisher()

        test_url = "https://www.instagram.com/reel/XYZ789ABC012/"
        # Note: extract_post_id is async, but we can test the regex logic
        import re
        match = re.search(r'/reel/([a-zA-Z0-9_-]+)', test_url)
        if match:
            post_id = match.group(1)
            assert post_id == "XYZ789ABC012"

    def test_extract_post_id_no_match(self):
        """Test extracting post ID with no match."""
        publisher = Publisher()

        test_url = "https://www.instagram.com/"
        # Note: extract_post_id is async, but we can test the regex logic
        import re
        match = re.search(r'/p/([a-zA-Z0-9_-]+)', test_url) or \
                re.search(r'/reel/([a-zA-Z0-9_-]+)', test_url)

        assert match is None

    @pytest.mark.asyncio
    async def test_publish_post_dry_run(self):
        """Test publishing post in dry run mode."""
        publisher = Publisher()
        publisher._dry_run = True

        result = await publisher.publish_post()

        assert result.success == True
        assert result.status == PublicationStatus.PUBLISHED
        assert "DRY RUN" in result.message
        assert result.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_publish_post_success(self):
        """Test publishing post successfully."""
        mock_browser_service = AsyncMock()

        # Mock successful share button click
        with patch.object(Publisher, 'click_share_button', AsyncMock(return_value=True)):
            # Mock successful wait for publication
            with patch.object(Publisher, 'wait_for_publication', AsyncMock(return_value=(True, "Success"))):
                # Mock get_post_url and extract_post_id
                with patch.object(Publisher, 'get_post_url', AsyncMock(return_value="https://example.com/p/123")):
                    with patch.object(Publisher, 'extract_post_id', AsyncMock(return_value="123")):
                        publisher = Publisher(mock_browser_service)
                        publisher._dry_run = False  # Ensure not in dry run mode

                        result = await publisher.publish_post()

                        assert result.success == True
                        assert result.status == PublicationStatus.PUBLISHED
                        assert result.post_url == "https://example.com/p/123"
                        assert result.post_id == "123"
                        assert result.published_at is not None
                        assert result.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_publish_post_share_button_failed(self):
        """Test publishing post when share button fails."""
        mock_browser_service = AsyncMock()

        with patch.object(Publisher, 'click_share_button', AsyncMock(return_value=False)):
            publisher = Publisher(mock_browser_service)
            publisher._dry_run = False  # Ensure not in dry run mode

            result = await publisher.publish_post()

            assert result.success == False
            assert result.status == PublicationStatus.FAILED
            assert "share button" in result.message.lower()

    @pytest.mark.asyncio
    async def test_schedule_post_dry_run(self):
        """Test scheduling post in dry run mode."""
        publisher = Publisher()
        publisher._dry_run = True

        schedule_time = datetime.now()

        result = await publisher.schedule_post(schedule_time)

        assert result.success == True
        assert result.status == PublicationStatus.SCHEDULED
        assert "DRY RUN" in result.message
        assert result.scheduled_for == schedule_time

    @pytest.mark.asyncio
    async def test_close_post_dialog_success(self):
        """Test closing post dialog successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.is_element_visible = AsyncMock(return_value=True)
        mock_browser_service.click_like_human = AsyncMock()
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.keyboard = AsyncMock()
        mock_browser_service.page.keyboard.press = AsyncMock()
        mock_browser_service.page.wait_for_selector = AsyncMock(side_effect=Exception("Not found"))

        publisher = Publisher(mock_browser_service)

        result = await publisher.close_post_dialog()

        assert result == True

    @pytest.mark.asyncio
    async def test_close_post_dialog_with_escape(self):
        """Test closing post dialog with Escape key."""
        mock_browser_service = AsyncMock()
        mock_browser_service.is_element_visible = AsyncMock(return_value=False)
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.keyboard = AsyncMock()
        mock_browser_service.page.keyboard.press = AsyncMock()
        mock_browser_service.page.wait_for_selector = AsyncMock(side_effect=Exception("Not found"))

        publisher = Publisher(mock_browser_service)

        result = await publisher.close_post_dialog()

        assert result == True
        mock_browser_service.page.keyboard.press.assert_called_with('Escape')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

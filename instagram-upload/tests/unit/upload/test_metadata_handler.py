"""
Unit tests for MetadataHandler.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
import re
from unittest.mock import Mock, patch, AsyncMock

from src.upload.metadata_handler import (
    MetadataHandler,
    VideoMetadata,
    MetadataError,
    CaptionValidationError,
    HashtagError,
    MetadataStatus
)


class TestVideoMetadata:
    """Tests for VideoMetadata class."""

    def test_valid_metadata(self):
        """Test valid metadata initialization."""
        metadata = VideoMetadata(
            caption="Beautiful sunset at the beach! 🌅",
            hashtags=["sunset", "beach", "nature"],
            location="Santa Monica Beach",
            alt_text="Sunset over ocean with silhouettes of palm trees",
            hide_like_count=True,
            disable_comments=False,
            schedule_time="2026-04-09T10:00:00"
        )

        assert metadata.caption == "Beautiful sunset at the beach! 🌅"
        assert metadata.hashtags == ["sunset", "beach", "nature"]
        assert metadata.location == "Santa Monica Beach"
        assert metadata.alt_text == "Sunset over ocean with silhouettes of palm trees"
        assert metadata.hide_like_count == True
        assert metadata.disable_comments == False
        assert metadata.schedule_time == "2026-04-09T10:00:00"

    def test_metadata_cleaning(self):
        """Test metadata cleaning during initialization."""
        metadata = VideoMetadata(
            caption="  Test caption with spaces  ",
            hashtags=["  #hashtag1  ", "#hashtag2", "hashtag3#"],
            location="  New York City  "
        )

        assert metadata.caption == "Test caption with spaces"
        assert metadata.hashtags == ["hashtag1", "hashtag2", "hashtag3"]
        assert metadata.location == "New York City"

    def test_hashtag_cleaning_special_characters(self):
        """Test hashtag cleaning with special characters."""
        metadata = VideoMetadata(
            hashtags=["#test-hashtag", "test@hashtag", "test!hashtag", "test hashtag"]
        )

        # Special characters should be removed
        assert metadata.hashtags == ["testhashtag", "testhashtag", "testhashtag", "testhashtag"]

    def test_validate_valid_metadata(self):
        """Test validation of valid metadata."""
        metadata = VideoMetadata(
            caption="Short caption",
            hashtags=["test", "example", "demo"],
            location="Test Location"
        )

        is_valid, errors = metadata.validate()

        assert is_valid == True
        assert errors == []

    def test_validate_caption_too_long(self):
        """Test validation with caption too long."""
        long_caption = "x" * 2201  # 2201 characters (Instagram limit is 2200)
        metadata = VideoMetadata(caption=long_caption)

        is_valid, errors = metadata.validate()

        assert is_valid == False
        assert any("too long" in error for error in errors)

    def test_validate_too_many_hashtags(self):
        """Test validation with too many hashtags."""
        many_hashtags = [f"tag{i}" for i in range(31)]  # 31 hashtags (limit is 30)
        metadata = VideoMetadata(hashtags=many_hashtags)

        is_valid, errors = metadata.validate()

        assert is_valid == False
        assert any("Too many hashtags" in error for error in errors)

    def test_validate_invalid_hashtag_characters(self):
        """Test validation with invalid hashtag characters."""
        metadata = VideoMetadata(hashtags=["test@hashtag", "test-hashtag"])

        is_valid, errors = metadata.validate()

        assert is_valid == False
        assert any("Invalid characters" in error for error in errors)

    def test_validate_empty_hashtag(self):
        """Test validation with empty hashtag."""
        metadata = VideoMetadata(hashtags=["", "test"])

        is_valid, errors = metadata.validate()

        assert is_valid == False
        assert any("empty" in error.lower() for error in errors)

    def test_format_caption_with_hashtags(self):
        """Test formatting caption with hashtags."""
        metadata = VideoMetadata(
            caption="Beautiful sunset",
            hashtags=["sunset", "nature", "photography"]
        )

        formatted = metadata.format_caption_with_hashtags()

        expected = "Beautiful sunset\n\n#sunset #nature #photography"
        assert formatted == expected

    def test_format_caption_only(self):
        """Test formatting with caption only (no hashtags)."""
        metadata = VideoMetadata(caption="Beautiful sunset")

        formatted = metadata.format_caption_with_hashtags()

        assert formatted == "Beautiful sunset"

    def test_format_hashtags_only(self):
        """Test formatting with hashtags only (no caption)."""
        metadata = VideoMetadata(hashtags=["sunset", "nature"])

        formatted = metadata.format_caption_with_hashtags()

        assert formatted == "#sunset #nature"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metadata = VideoMetadata(
            caption="Test",
            hashtags=["test1", "test2"],
            location="Location",
            alt_text="Alt text",
            hide_like_count=True,
            disable_comments=False
        )

        data = metadata.to_dict()

        assert data['caption'] == "Test"
        assert data['hashtags'] == ["test1", "test2"]
        assert data['location'] == "Location"
        assert data['alt_text'] == "Alt text"
        assert data['hide_like_count'] == True
        assert data['disable_comments'] == False
        assert 'formatted_caption' in data

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'caption': 'Test',
            'hashtags': ['test1', 'test2'],
            'location': 'Location',
            'alt_text': 'Alt text',
            'hide_like_count': True,
            'disable_comments': False,
            'schedule_time': '2026-04-09T10:00:00'
        }

        metadata = VideoMetadata.from_dict(data)

        assert metadata.caption == "Test"
        assert metadata.hashtags == ["test1", "test2"]
        assert metadata.location == "Location"
        assert metadata.alt_text == "Alt text"
        assert metadata.hide_like_count == True
        assert metadata.disable_comments == False
        assert metadata.schedule_time == "2026-04-09T10:00:00"


class TestMetadataHandler:
    """Tests for MetadataHandler class."""

    def test_initialization(self):
        """Test metadata handler initialization."""
        with patch.dict(os.environ, {
            'INSTAGRAM_DEFAULT_HASHTAGS': '#aireels,#ai,#video,#automation'
        }, clear=True):
            handler = MetadataHandler()

            assert handler._default_hashtags == ["aireels", "ai", "video", "automation"]

    def test_load_default_hashtags_empty(self):
        """Test loading default hashtags when empty."""
        with patch.dict(os.environ, {}, clear=True):
            handler = MetadataHandler()

            assert handler._default_hashtags == []

    def test_load_default_hashtags_with_commas(self):
        """Test loading default hashtags with commas."""
        with patch.dict(os.environ, {
            'INSTAGRAM_DEFAULT_HASHTAGS': 'tag1, tag2, #tag3'
        }, clear=True):
            handler = MetadataHandler()

            assert handler._default_hashtags == ["tag1", "tag2", "tag3"]

    def test_enhance_metadata_with_auto_add(self):
        """Test enhancing metadata with auto-add hashtags."""
        with patch.dict(os.environ, {
            'INSTAGRAM_DEFAULT_HASHTAGS': 'default1,default2'
        }, clear=True):
            handler = MetadataHandler()

            original = VideoMetadata(
                caption="Test",
                hashtags=["custom1"]
            )

            enhanced = handler.enhance_metadata(original, auto_add_hashtags=True)

            assert "custom1" in enhanced.hashtags
            assert "default1" in enhanced.hashtags
            assert "default2" in enhanced.hashtags
            assert len(enhanced.hashtags) == 3

    def test_enhance_metadata_without_auto_add(self):
        """Test enhancing metadata without auto-add hashtags."""
        with patch.dict(os.environ, {
            'INSTAGRAM_DEFAULT_HASHTAGS': 'default1,default2'
        }, clear=True):
            handler = MetadataHandler()

            original = VideoMetadata(
                caption="Test",
                hashtags=["custom1"]
            )

            enhanced = handler.enhance_metadata(original, auto_add_hashtags=False)

            assert enhanced.hashtags == ["custom1"]  # No default hashtags added

    def test_enhance_metadata_limit_hashtags(self):
        """Test enhancing metadata with hashtag limit."""
        with patch.dict(os.environ, {
            'INSTAGRAM_DEFAULT_HASHTAGS': 'default'
        }, clear=True):
            handler = MetadataHandler()

            # Create 30 custom hashtags (at limit)
            custom_hashtags = [f"tag{i}" for i in range(30)]
            original = VideoMetadata(hashtags=custom_hashtags)

            enhanced = handler.enhance_metadata(original, auto_add_hashtags=True)

            # Should be limited to 30 total
            assert len(enhanced.hashtags) == 30
            # Default hashtag should NOT be added (would exceed limit)
            assert "default" not in enhanced.hashtags

    @pytest.mark.asyncio
    async def test_enter_caption_success(self):
        """Test entering caption successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=True)
        mock_browser_service.type_like_human = AsyncMock()
        mock_browser_service.take_screenshot = AsyncMock()

        handler = MetadataHandler(mock_browser_service)

        result = await handler.enter_caption("Test caption")

        assert result == True
        mock_browser_service.type_like_human.assert_called_once()

    @pytest.mark.asyncio
    async def test_enter_caption_field_not_found(self):
        """Test entering caption when field not found."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=False)
        mock_browser_service.take_screenshot = AsyncMock()

        handler = MetadataHandler(mock_browser_service)

        result = await handler.enter_caption("Test caption")

        assert result == False
        mock_browser_service.take_screenshot.assert_called_with("caption_field_missing")

    @pytest.mark.asyncio
    async def test_add_hashtags_success(self):
        """Test adding hashtags successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=True)
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.click = AsyncMock()
        mock_browser_service.page.keyboard = AsyncMock()
        mock_browser_service.page.keyboard.press = AsyncMock()
        mock_browser_service.page.evaluate = AsyncMock(return_value="")
        mock_browser_service.type_like_human = AsyncMock()
        mock_browser_service.take_screenshot = AsyncMock()

        handler = MetadataHandler(mock_browser_service)

        result = await handler.add_hashtags(["test1", "test2"])

        assert result == True

    @pytest.mark.asyncio
    async def test_add_hashtags_empty_list(self):
        """Test adding empty hashtag list."""
        handler = MetadataHandler()

        result = await handler.add_hashtags([])

        assert result == True  # Should return True for empty list

    @pytest.mark.asyncio
    async def test_add_location_success(self):
        """Test adding location successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(side_effect=[True, True, True])
        mock_browser_service.click_like_human = AsyncMock()
        mock_browser_service.type_like_human = AsyncMock()
        mock_browser_service.is_element_visible = AsyncMock(return_value=True)
        mock_browser_service.take_screenshot = AsyncMock()

        handler = MetadataHandler(mock_browser_service)

        result = await handler.add_location("Test Location")

        assert result == True

    @pytest.mark.asyncio
    async def test_add_location_button_not_found(self):
        """Test adding location when button not found (optional)."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=False)
        mock_browser_service.take_screenshot = AsyncMock()

        handler = MetadataHandler(mock_browser_service)

        result = await handler.add_location("Test Location")

        # Location is optional, so should return True even if button not found
        assert result == True

    @pytest.mark.asyncio
    async def test_configure_advanced_options_nothing_to_configure(self):
        """Test configuring advanced options with nothing to configure."""
        handler = MetadataHandler()

        result = await handler.configure_advanced_options()

        assert result == True

    @pytest.mark.asyncio
    async def test_enter_all_metadata_success(self):
        """Test entering all metadata successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=True)
        mock_browser_service.type_like_human = AsyncMock()
        mock_browser_service.take_screenshot = AsyncMock()
        mock_browser_service.click_like_human = AsyncMock()
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.keyboard = AsyncMock()
        mock_browser_service.page.keyboard.press = AsyncMock()
        mock_browser_service.page.evaluate = AsyncMock(return_value="")
        mock_browser_service.is_element_visible = AsyncMock(return_value=False)

        handler = MetadataHandler(mock_browser_service)

        metadata = VideoMetadata(
            caption="Test caption",
            hashtags=["test1", "test2"],
            location="Test Location"
        )

        result = await handler.enter_all_metadata(metadata)

        assert result == True

    @pytest.mark.asyncio
    async def test_enter_all_metadata_validation_failed(self):
        """Test entering all metadata with validation failure."""
        handler = MetadataHandler()

        # Create invalid metadata (caption too long)
        long_caption = "x" * 2201
        metadata = VideoMetadata(caption=long_caption)

        result = await handler.enter_all_metadata(metadata)

        assert result == False

    @pytest.mark.asyncio
    async def test_click_next_to_share_success(self):
        """Test clicking next to share successfully."""
        mock_browser_service = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(side_effect=[True, True])
        mock_browser_service.click_like_human = AsyncMock()
        mock_browser_service.take_screenshot = AsyncMock()

        handler = MetadataHandler(mock_browser_service)

        result = await handler.click_next_to_share()

        assert result == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
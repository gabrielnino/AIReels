import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
"""
Unit tests for VideoUploader.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.upload.video_uploader import (
    VideoUploader,
    VideoInfo,
    UploadResult,
    UploadStatus,
    VideoValidationError,
    UploadError
)


class TestVideoInfo:
    """Tests for VideoInfo class."""

    def test_valid_video_info(self):
        """Test valid video info initialization."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            video_info = VideoInfo(
                path=Path(tmp_path),
                caption="Test caption",
                hashtags=["test", "video"],
                location="Test Location",
                duration_seconds=60.5,
                size_mb=10.5,
                format="mp4"
            )

            assert video_info.path == Path(tmp_path)
            assert video_info.caption == "Test caption"
            assert video_info.hashtags == ["test", "video"]
            assert video_info.location == "Test Location"
            assert video_info.duration_seconds == 60.5
            assert video_info.size_mb == 10.5
            assert video_info.format == "mp4"
        finally:
            os.unlink(tmp_path)

    def test_video_info_with_string_path(self):
        """Test video info with string path."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            video_info = VideoInfo(path=tmp_path)
            assert isinstance(video_info.path, Path)
            assert str(video_info.path) == tmp_path
        finally:
            os.unlink(tmp_path)

    def test_video_info_nonexistent_file(self):
        """Test video info with nonexistent file."""
        with pytest.raises(VideoValidationError, match="Video file not found"):
            VideoInfo(path="/nonexistent/file.mp4")

    def test_validate_valid_video(self):
        """Test validation of valid video."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            # Write some data to make file have size
            tmp.write(b'test data' * 1000)
            tmp.flush()
            tmp_path = tmp.name

        try:
            with patch.dict(os.environ, {
                'INSTAGRAM_MAX_VIDEO_SIZE_MB': '100',
                'INSTAGRAM_ALLOWED_FORMATS': 'mp4,mov'
            }, clear=True):
                video_info = VideoInfo(path=tmp_path)
                is_valid, errors = video_info.validate()

                assert is_valid == True
                assert errors == []
                assert video_info.size_mb is not None
                assert video_info.format == "mp4"
        finally:
            os.unlink(tmp_path)

    def test_validate_invalid_format(self):
        """Test validation with invalid format."""
        with tempfile.NamedTemporaryFile(suffix='.avi', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch.dict(os.environ, {
                'INSTAGRAM_ALLOWED_FORMATS': 'mp4,mov'
            }, clear=True):
                video_info = VideoInfo(path=tmp_path)
                is_valid, errors = video_info.validate()

                assert is_valid == False
                assert any("not allowed" in error for error in errors)
                assert video_info.format == "avi"
        finally:
            os.unlink(tmp_path)

    def test_validate_file_too_large(self):
        """Test validation with file too large."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            # Create a "large" file (1MB)
            tmp.write(b'x' * (1024 * 1024))  # 1MB
            tmp.flush()
            tmp_path = tmp.name

        try:
            with patch.dict(os.environ, {
                'INSTAGRAM_MAX_VIDEO_SIZE_MB': '0.5'  # 0.5MB limit
            }, clear=True):
                video_info = VideoInfo(path=tmp_path)
                is_valid, errors = video_info.validate()

                assert is_valid == False
                assert any("exceeds maximum" in error for error in errors)
        finally:
            os.unlink(tmp_path)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        # Create a temporary file that actually exists
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            video_info = VideoInfo(
                path=Path(tmp_path),
                caption="Test",
                hashtags=["test"],
                location="Location",
                duration_seconds=60,
                size_mb=10,
                format="mp4"
            )

            data = video_info.to_dict()

            # Note: to_dict() converts Path to string
            assert data['path'] == tmp_path
            assert data['caption'] == "Test"
            assert data['hashtags'] == ["test"]
            assert data['location'] == "Location"
            assert data['duration_seconds'] == 60
            assert data['size_mb'] == 10
            assert data['format'] == "mp4"
        finally:
            os.unlink(tmp_path)


class TestVideoUploader:
    """Tests for VideoUploader class."""

    def test_initialization(self):
        """Test uploader initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                'INSTAGRAM_VIDEO_INPUT_DIR': os.path.join(temp_dir, 'input'),
                'INSTAGRAM_VIDEO_PROCESSED_DIR': os.path.join(temp_dir, 'processed'),
                'INSTAGRAM_VIDEO_FAILED_DIR': os.path.join(temp_dir, 'failed'),
                'INSTAGRAM_UPLOAD_TIMEOUT': '300',
                'INSTAGRAM_UPLOAD_MAX_RETRIES': '3'
            }, clear=True):
                uploader = VideoUploader()

                assert uploader.input_dir == Path(os.path.join(temp_dir, 'input'))
                assert uploader.processed_dir == Path(os.path.join(temp_dir, 'processed'))
                assert uploader.failed_dir == Path(os.path.join(temp_dir, 'failed'))
                assert uploader._upload_timeout == 300
                assert uploader._max_retries == 3

                # Check directories were created
                assert uploader.input_dir.exists()
                assert uploader.processed_dir.exists()
                assert uploader.failed_dir.exists()

    @pytest.mark.asyncio
    async def test_ensure_authenticated_with_browser_service(self):
        """Test ensure_authenticated with provided browser service."""
        mock_browser_service = AsyncMock()
        mock_browser_service.page = AsyncMock()
        mock_browser_service.page.wait_for_selector = AsyncMock()

        uploader = VideoUploader(browser_service=mock_browser_service)

        # Mock successful authentication check
        mock_browser_service.page.wait_for_selector.return_value = True

        result = await uploader.ensure_authenticated()

        assert result == True
        assert uploader._is_authenticated == True
        mock_browser_service.page.wait_for_selector.assert_called_with(
            'svg[aria-label="Home"]', timeout=5000
        )

    @pytest.mark.asyncio
    async def test_ensure_authenticated_without_browser_service(self):
        """Test ensure_authenticated creating its own browser service."""
        with patch('src.auth.browser_service.BrowserService') as mock_browser_class:
            mock_browser_service = AsyncMock()
            mock_browser_class.return_value = mock_browser_service

            mock_browser_service.page = AsyncMock()
            mock_browser_service.page.wait_for_selector = AsyncMock(return_value=True)
            mock_browser_service.initialize = AsyncMock()

            uploader = VideoUploader()

            result = await uploader.ensure_authenticated()

            assert result == True
            assert uploader._is_authenticated == True
            assert uploader.browser_service == mock_browser_service
            mock_browser_service.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_navigate_to_upload_not_authenticated(self):
        """Test navigate_to_upload when not authenticated."""
        uploader = VideoUploader()

        with patch.object(uploader, 'ensure_authenticated', AsyncMock(return_value=False)):
            result = await uploader.navigate_to_upload()

            assert result == False

    @pytest.mark.asyncio
    async def test_select_video_file(self):
        """Test select_video_file method."""
        mock_browser_service = AsyncMock()
        mock_browser_service.page = AsyncMock()
        mock_browser_service.wait_for_element = AsyncMock(return_value=True)
        mock_browser_service.is_element_visible = AsyncMock(return_value=False)
        mock_browser_service.get_element_text = AsyncMock()
        mock_browser_service.take_screenshot = AsyncMock()

        uploader = VideoUploader(browser_service=mock_browser_service)

        test_video_path = Path("/test/video.mp4")

        # Mock successful file selection
        mock_browser_service.page.set_input_files = AsyncMock()

        result = await uploader.select_video_file(test_video_path)

        assert result == True
        mock_browser_service.page.set_input_files.assert_called_with(
            'input[type="file"][accept*="video"]', str(test_video_path)
        )

    @pytest.mark.asyncio
    async def test_upload_video_validation_failed(self):
        """Test upload_video when validation fails."""
        uploader = VideoUploader()

        # Create video info that will fail validation
        with tempfile.NamedTemporaryFile(suffix='.avi', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch.dict(os.environ, {
                'INSTAGRAM_ALLOWED_FORMATS': 'mp4,mov'
            }, clear=True):
                video_info = VideoInfo(path=tmp_path)
                result = await uploader.upload_video(video_info)

                assert result.success == False
                assert result.status == UploadStatus.FAILED
                assert "not allowed" in result.message
                assert len(result.errors) > 0
        finally:
            os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_move_processed_video_success(self):
        """Test moving video to processed directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                'INSTAGRAM_VIDEO_PROCESSED_DIR': os.path.join(temp_dir, 'processed'),
                'INSTAGRAM_VIDEO_FAILED_DIR': os.path.join(temp_dir, 'failed')
            }, clear=True):
                uploader = VideoUploader()

                # Create test video file
                test_video_path = Path(temp_dir) / "test_video.mp4"
                test_video_path.write_text("test content")

                video_info = VideoInfo(path=test_video_path)

                # Move to processed
                new_path = await uploader.move_processed_video(video_info, success=True)

                assert new_path != test_video_path
                assert new_path.parent == uploader.processed_dir
                assert "test_video.mp4" in str(new_path)
                assert new_path.exists()

                # Original should still exist (we copy, not move)
                assert test_video_path.exists()

    @pytest.mark.asyncio
    async def test_upload_video_with_retry_success_first_try(self):
        """Test upload_video_with_retry with success on first try."""
        uploader = VideoUploader()

        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            video_info = VideoInfo(path=tmp_path)

            # Mock successful upload
            with patch.object(uploader, 'upload_video', AsyncMock()) as mock_upload:
                mock_result = UploadResult(
                    success=True,
                    video_info=video_info,
                    status=UploadStatus.COMPLETED,
                    message="Success"
                )
                mock_upload.return_value = mock_result

                # Mock move_processed_video
                with patch.object(uploader, 'move_processed_video', AsyncMock()):
                    result = await uploader.upload_video_with_retry(video_info)

                    assert result == mock_result
                    mock_upload.assert_called_once_with(video_info)
        finally:
            os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_upload_video_with_retry_failure_all_attempts(self):
        """Test upload_video_with_retry with all attempts failing."""
        uploader = VideoUploader()
        uploader._max_retries = 2  # 2 retries = 3 total attempts

        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            video_info = VideoInfo(path=tmp_path)

            # Mock failing upload
            with patch.object(uploader, 'upload_video', AsyncMock()) as mock_upload:
                mock_result = UploadResult(
                    success=False,
                    video_info=video_info,
                    status=UploadStatus.FAILED,
                    message="Failed"
                )
                mock_upload.return_value = mock_result

                # Mock move_processed_video for failure
                with patch.object(uploader, 'move_processed_video', AsyncMock()):
                    # Mock browser service reload
                    uploader.browser_service = AsyncMock()
                    uploader.browser_service.reload_page = AsyncMock()

                    result = await uploader.upload_video_with_retry(video_info)

                    assert result == mock_result
                    # Should be called 3 times (initial + 2 retries)
                    assert mock_upload.call_count == 3
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
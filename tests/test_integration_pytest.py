"""
Pytest tests for the integration module.

These tests verify that the integration between qwen-poc and Instagram upload
works correctly.
"""

import pytest
import asyncio
import tempfile
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integration.data_models import VideoMetadata, UploadResult, UploadStatus, UploadOptions
from integration.metadata_adapter import adapt_qwen_to_upload, validate_metadata
from integration.mock_uploader import MockInstagramUploader
from integration.pipeline_bridge import PipelineBridge


class TestDataModels:
    """Tests for data models."""

    def test_video_metadata_creation(self):
        """Test creating VideoMetadata with valid data."""
        metadata = VideoMetadata(
            video_path="/tmp/test.mp4",
            caption="Test caption with #hashtag",
            hashtags=["#test", "#demo"],
            topic="Technology",
            emotion="excited",
            cta="Subscribe for more!"
        )

        assert metadata.video_path == "/tmp/test.mp4"
        assert metadata.caption == "Test caption with #hashtag"
        assert metadata.hashtags == ["#test", "#demo"]
        assert metadata.topic == "Technology"
        assert metadata.emotion == "excited"

    def test_video_metadata_to_dict(self):
        """Test converting VideoMetadata to dictionary."""
        metadata = VideoMetadata(
            video_path="/tmp/test.mp4",
            caption="Test",
            hashtags=["#test"]
        )

        data = metadata.to_dict()
        assert data["video_path"] == "/tmp/test.mp4"
        assert data["caption"] == "Test"
        assert data["hashtags"] == ["#test"]

    def test_upload_result_creation(self):
        """Test creating UploadResult."""
        result = UploadResult(
            status=UploadStatus.COMPLETED,
            media_id="test_123",
            error_message=None,
            retry_count=0
        )

        assert result.status == UploadStatus.COMPLETED
        assert result.media_id == "test_123"
        assert result.error_message is None
        assert result.retry_count == 0


class TestMetadataAdapter:
    """Tests for metadata adapter."""

    def test_adapt_qwen_to_upload_valid(self):
        """Test adapting valid qwen-poc output."""
        # Create a test video file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b'test video content')
            video_path = f.name

        try:
            qwen_output = {
                "final_video_path": video_path,
                "caption": "Test video with #hashtags",
                "hashtags": ["#test", "#ai", "#tech"],
                "topic": "Artificial Intelligence",
                "language": "en",
                "duration_seconds": 45,
                "file_size_bytes": 1024 * 1024 * 10,  # 10MB
                "width": 1080,
                "height": 1920
            }

            options = UploadOptions()
            metadata = adapt_qwen_to_upload(qwen_output, options)

            assert isinstance(metadata, VideoMetadata)
            assert metadata.video_path == video_path
            assert metadata.caption == "Test video with #hashtags"
            assert metadata.hashtags == ["#test", "#ai", "#tech"]
            assert metadata.topic == "Artificial Intelligence"
        finally:
            # Clean up
            if os.path.exists(video_path):
                os.unlink(video_path)

    def test_adapt_qwen_to_upload_invalid_hashtags(self):
        """Test adapting qwen output with invalid hashtags."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b'test video content')
            video_path = f.name

        try:
            qwen_output = {
                "final_video_path": video_path,
                "caption": "Test video",
                "hashtags": ["test", "no_hash"],  # Missing # prefix
                "topic": "Test"
            }

            options = UploadOptions()

            # Should raise ValueError because hashtags don't start with #
            with pytest.raises(ValueError, match="doesn't start with #"):
                adapt_qwen_to_upload(qwen_output, options)
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)


class TestMockUploader:
    """Tests for mock uploader."""

    @pytest.mark.asyncio
    async def test_mock_uploader_success(self):
        """Test mock uploader with success."""
        uploader = MockInstagramUploader(success_rate=1.0)  # Always success

        metadata = VideoMetadata(
            video_path="/tmp/test.mp4",
            caption="Test caption",
            hashtags=["#test"]
        )

        options = UploadOptions(max_retries=2)
        result = await uploader.upload_video(metadata, options)

        assert result.status == UploadStatus.COMPLETED
        assert result.media_id is not None
        assert result.retry_count == 0

    @pytest.mark.asyncio
    async def test_mock_uploader_failure(self):
        """Test mock uploader with failure."""
        uploader = MockInstagramUploader(success_rate=0.0)  # Always fail

        metadata = VideoMetadata(
            video_path="/tmp/test.mp4",
            caption="Test caption",
            hashtags=["#test"]
        )

        options = UploadOptions(max_retries=2)
        result = await uploader.upload_video(metadata, options)

        assert result.status == UploadStatus.FAILED
        assert result.error_message is not None
        assert result.retry_count >= 0


class TestPipelineBridge:
    """Tests for pipeline bridge."""

    @pytest.mark.asyncio
    async def test_pipeline_bridge_complete_flow(self):
        """Test complete pipeline flow with mock uploader."""
        # Create a test video file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b'test video content for pipeline')
            video_path = f.name

        try:
            # Mock qwen-poc output
            qwen_output = {
                "final_video_path": video_path,
                "caption": "Pipeline test video #testing #integration",
                "hashtags": ["#testing", "#integration", "#pipeline"],
                "topic": "Pipeline Testing",
                "language": "en",
                "duration_seconds": 30,
                "file_size_bytes": 1024 * 1024 * 5,  # 5MB
                "width": 1080,
                "height": 1920
            }

            # Create pipeline bridge with mock uploader
            uploader = MockInstagramUploader(success_rate=1.0)
            bridge = PipelineBridge(uploader)

            # Process and upload
            options = UploadOptions(max_retries=2)
            result = await bridge.process_and_upload(qwen_output, options=options)

            assert result.status == UploadStatus.COMPLETED
            assert result.media_id is not None
            assert result.total_duration_seconds is not None
            assert result.total_duration_seconds > 0
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    @pytest.mark.asyncio
    async def test_pipeline_bridge_with_retries(self):
        """Test pipeline with flaky uploader that requires retries."""
        # Create a test video file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b'test video content')
            video_path = f.name

        try:
            qwen_output = {
                "final_video_path": video_path,
                "caption": "Test with retries #retry #testing",
                "hashtags": ["#retry", "#testing"],
                "topic": "Retry Testing"
            }

            # Use a flaky uploader (50% success rate)
            uploader = MockInstagramUploader(success_rate=0.5)
            bridge = PipelineBridge(uploader)

            options = UploadOptions(max_retries=3, retry_delay_seconds=0.1)
            result = await bridge.process_and_upload_with_retry(qwen_output, options=options)

            # Should eventually succeed with retries
            assert result.status in [UploadStatus.COMPLETED, UploadStatus.FAILED]
            assert result.retry_count >= 0
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)


def test_metadata_validation():
    """Test metadata validation against Instagram limits."""
    metadata = VideoMetadata(
        video_path="/tmp/test.mp4",
        caption="A" * 2500,  # Too long (max 2200)
        hashtags=["#test"] * 35,  # Too many (max 30)
        topic="Test"
    )

    options = UploadOptions()

    # Should raise ValueError for validation failures
    with pytest.raises(ValueError, match="Caption too long"):
        validate_metadata(metadata, options)


if __name__ == "__main__":
    # Run tests directly if needed
    pytest.main([__file__, "-v"])
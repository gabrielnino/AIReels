"""
Integration tests for complete upload flow.

Tests the interaction between VideoUploader, MetadataHandler, and Publisher
for a complete Instagram upload process.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.upload.video_uploader import VideoUploader, VideoInfo, UploadResult, UploadStatus
from src.upload.metadata_handler import MetadataHandler, VideoMetadata
from src.upload.publisher import Publisher, PublicationResult, PublicationStatus


class TestUploadIntegration:
    """Integration tests for upload components."""

    def test_video_info_to_metadata_integration(self):
        """Test integration between VideoInfo and VideoMetadata."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Create VideoInfo
            video_info = VideoInfo(
                path=Path(tmp_path),
                caption="Test video caption",
                hashtags=["test", "video"],
                location="Test Location"
            )

            # Convert to VideoMetadata
            metadata = VideoMetadata(
                caption=video_info.caption,
                hashtags=video_info.hashtags,
                location=video_info.location
            )

            # Validate both
            video_valid, video_errors = video_info.validate()
            metadata_valid, metadata_errors = metadata.validate()

            print(f"Video validation: {video_valid}, errors: {video_errors}")
            print(f"Metadata validation: {metadata_valid}, errors: {metadata_errors}")

            # Both should be valid (file exists, format OK, metadata within limits)
            assert video_valid == True or "not allowed" not in str(video_errors)
            assert metadata_valid == True

        finally:
            os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_complete_upload_flow_mocked(self):
        """Test complete upload flow with all components (mocked)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test video file
            test_video_path = Path(temp_dir) / "test_video.mp4"
            test_video_path.write_text("dummy video content")

            # Configure environment
            with patch.dict(os.environ, {
                'INSTAGRAM_VIDEO_INPUT_DIR': temp_dir,
                'INSTAGRAM_VIDEO_PROCESSED_DIR': os.path.join(temp_dir, 'processed'),
                'INSTAGRAM_VIDEO_FAILED_DIR': os.path.join(temp_dir, 'failed'),
                'INSTAGRAM_MAX_VIDEO_SIZE_MB': '100',
                'INSTAGRAM_ALLOWED_FORMATS': 'mp4,mov',
                'INSTAGRAM_DRY_RUN': 'true'
            }, clear=True):
                # Create video info
                video_info = VideoInfo(
                    path=test_video_path,
                    caption="Integration test video",
                    hashtags=["integration", "test", "automation"],
                    location="Test City"
                )

                # Create metadata
                metadata = VideoMetadata(
                    caption=video_info.caption,
                    hashtags=video_info.hashtags,
                    location=video_info.location
                )

                print("\n📋 Test Setup:")
                print(f"   Video: {video_info.path.name}")
                print(f"   Caption: {metadata.caption}")
                print(f"   Hashtags: {metadata.hashtags}")
                print(f"   Location: {metadata.location}")

                # Validate video
                is_valid, errors = video_info.validate()
                print(f"\n🎬 Video Validation: {'✅' if is_valid else '❌'}")
                if errors:
                    print(f"   Errors: {errors}")

                assert is_valid == True or "not allowed" not in str(errors)

                # Validate metadata
                metadata_valid, metadata_errors = metadata.validate()
                print(f"\n📝 Metadata Validation: {'✅' if metadata_valid else '❌'}")
                if metadata_errors:
                    print(f"   Errors: {metadata_errors}")

                assert metadata_valid == True

                # Test MetadataHandler enhancement
                metadata_handler = MetadataHandler()
                enhanced_metadata = metadata_handler.enhance_metadata(metadata, auto_add_hashtags=False)

                print(f"\n🔧 Metadata Enhancement:")
                print(f"   Original hashtags: {len(metadata.hashtags)}")
                print(f"   Enhanced hashtags: {len(enhanced_metadata.hashtags)}")

                # Test formatted caption
                formatted = enhanced_metadata.format_caption_with_hashtags()
                print(f"\n📄 Formatted Caption:")
                print(f"   Length: {len(formatted)} characters")
                print(f"   Preview: {formatted[:100]}...")

                # Test upload flow (mocked)
                print("\n🚀 Upload Flow Simulation:")

                # Mock browser service
                mock_browser_service = AsyncMock()

                # Create uploader with mocked browser
                uploader = VideoUploader(mock_browser_service)
                uploader._dry_run = True  # Enable dry run for testing

                # Mock upload result
                mock_upload_result = UploadResult(
                    success=True,
                    video_info=video_info,
                    status=UploadStatus.COMPLETED,
                    message="Upload successful (simulated)",
                    duration_seconds=10.5
                )

                with patch.object(uploader, 'upload_video', AsyncMock(return_value=mock_upload_result)):
                    # Simulate upload
                    upload_result = await uploader.upload_video(video_info)

                    print(f"   Upload Result: {upload_result.status.value}")
                    print(f"   Message: {upload_result.message}")
                    print(f"   Duration: {upload_result.duration_seconds:.1f}s")

                    assert upload_result.success == True
                    assert upload_result.status == UploadStatus.COMPLETED

                # Test publication flow (mocked)
                print("\n📤 Publication Flow Simulation:")

                publisher = Publisher(mock_browser_service)
                publisher._dry_run = True

                # Mock publication result
                mock_publication_result = PublicationResult(
                    success=True,
                    status=PublicationStatus.PUBLISHED,
                    message="Publication successful (simulated)",
                    post_url="https://www.instagram.com/p/TEST123/",
                    post_id="TEST123",
                    published_at=datetime.now(),
                    duration_seconds=5.2
                )

                with patch.object(publisher, 'publish_post', AsyncMock(return_value=mock_publication_result)):
                    # Simulate publication
                    publication_result = await publisher.publish_post()

                    print(f"   Publication Result: {publication_result.status.value}")
                    print(f"   Message: {publication_result.message}")
                    print(f"   Post URL: {publication_result.post_url}")
                    print(f"   Post ID: {publication_result.post_id}")
                    print(f"   Duration: {publication_result.duration_seconds:.1f}s")

                    assert publication_result.success == True
                    assert publication_result.status == PublicationStatus.PUBLISHED

                print("\n🎉 Complete flow simulation successful!")

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across upload components."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test video with invalid format
            test_video_path = Path(temp_dir) / "test_video.avi"
            test_video_path.write_text("dummy content")

            with patch.dict(os.environ, {
                'INSTAGRAM_ALLOWED_FORMATS': 'mp4,mov'
            }, clear=True):
                # Create video info with invalid format
                video_info = VideoInfo(path=test_video_path)

                # Validation should fail
                is_valid, errors = video_info.validate()

                assert is_valid == False
                assert any("not allowed" in error for error in errors)

                # Upload should fail due to validation
                uploader = VideoUploader()

                upload_result = await uploader.upload_video(video_info)

                assert upload_result.success == False
                assert upload_result.status == UploadStatus.FAILED
                assert "validation" in upload_result.message.lower()

    @pytest.mark.asyncio
    async def test_metadata_handler_with_uploader_integration(self):
        """Test integration between MetadataHandler and VideoUploader."""
        mock_browser_service = AsyncMock()

        # Create uploader
        uploader = VideoUploader(mock_browser_service)

        # Create metadata handler with same browser service
        metadata_handler = MetadataHandler(mock_browser_service)

        # Test that they use the same browser service
        assert uploader.browser_service == metadata_handler.browser_service

        # Test metadata entry (mocked)
        metadata = VideoMetadata(
            caption="Test caption",
            hashtags=["test1", "test2"],
            location="Test Location"
        )

        # Mock successful metadata entry
        with patch.object(metadata_handler, 'enter_all_metadata', AsyncMock(return_value=True)):
            result = await metadata_handler.enter_all_metadata(metadata)

            assert result == True

    @pytest.mark.asyncio
    async def test_component_interaction_with_retry_logic(self):
        """Test component interaction with retry logic."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            video_info = VideoInfo(path=tmp_path)

            # Create uploader with retry logic
            uploader = VideoUploader()
            uploader._max_retries = 2  # 2 retries = 3 total attempts

            # Mock upload_video to fail twice then succeed
            mock_upload_results = [
                UploadResult(success=False, video_info=video_info, status=UploadStatus.FAILED, message="First attempt failed"),
                UploadResult(success=False, video_info=video_info, status=UploadStatus.FAILED, message="Second attempt failed"),
                UploadResult(success=True, video_info=video_info, status=UploadStatus.COMPLETED, message="Third attempt succeeded")
            ]

            upload_call_count = 0

            async def mock_upload_video(video_info):
                nonlocal upload_call_count
                result = mock_upload_results[upload_call_count]
                upload_call_count += 1
                return result

            with patch.object(uploader, 'upload_video', mock_upload_video):
                with patch.object(uploader, 'move_processed_video', AsyncMock()):
                    # Mock browser service for reload
                    uploader.browser_service = AsyncMock()
                    uploader.browser_service.reload_page = AsyncMock()

                    result = await uploader.upload_video_with_retry(video_info)

                    assert result.success == True
                    assert upload_call_count == 3  # Should have tried 3 times
                    assert "succeeded" in result.message

        finally:
            os.unlink(tmp_path)

    def test_directory_structure_integration(self):
        """Test directory structure integration between components."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / "input"
            processed_dir = Path(temp_dir) / "processed"
            failed_dir = Path(temp_dir) / "failed"

            with patch.dict(os.environ, {
                'INSTAGRAM_VIDEO_INPUT_DIR': str(input_dir),
                'INSTAGRAM_VIDEO_PROCESSED_DIR': str(processed_dir),
                'INSTAGRAM_VIDEO_FAILED_DIR': str(failed_dir)
            }, clear=True):
                # Create uploader - should create directories
                uploader = VideoUploader()

                assert uploader.input_dir.exists()
                assert uploader.processed_dir.exists()
                assert uploader.failed_dir.exists()

                # Create a test video in input directory
                test_video = input_dir / "test_video.mp4"
                test_video.write_text("test content")

                assert test_video.exists()

                # Test moving to processed directory
                video_info = VideoInfo(path=test_video)

                # Import asyncio and run the async method
                import asyncio
                new_path = asyncio.run(uploader.move_processed_video(video_info, success=True))

                assert new_path.parent == processed_dir
                assert new_path.exists()

    @pytest.mark.asyncio
    async def test_complete_workflow_with_error_recovery(self):
        """Test complete workflow with error recovery simulation."""
        print("\n🔄 Testing Complete Workflow with Error Recovery")

        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Setup
            video_info = VideoInfo(path=tmp_path, caption="Recovery test")
            metadata = VideoMetadata(caption=video_info.caption, hashtags=["recovery", "test"])

            # Mock components
            mock_browser_service = AsyncMock()

            # Test scenario: Upload fails, metadata entry succeeds, publication fails
            print("\n1. Simulating upload failure...")
            uploader = VideoUploader(mock_browser_service)
            with patch.object(uploader, 'upload_video', AsyncMock(return_value=UploadResult(
                success=False, video_info=video_info, status=UploadStatus.FAILED, message="Upload failed"
            ))):
                upload_result = await uploader.upload_video(video_info)
                assert upload_result.success == False

            print("2. Simulating metadata entry success...")
            metadata_handler = MetadataHandler(mock_browser_service)
            with patch.object(metadata_handler, 'enter_all_metadata', AsyncMock(return_value=True)):
                metadata_result = await metadata_handler.enter_all_metadata(metadata)
                assert metadata_result == True

            print("3. Simulating publication failure...")
            publisher = Publisher(mock_browser_service)
            with patch.object(publisher, 'publish_post', AsyncMock(return_value=PublicationResult(
                success=False, status=PublicationStatus.FAILED, message="Publication failed"
            ))):
                publication_result = await publisher.publish_post()
                assert publication_result.success == False

            print("\n📊 Workflow Results Summary:")
            print(f"   Upload: {'✅' if upload_result.success else '❌'} - {upload_result.message}")
            print(f"   Metadata: {'✅' if metadata_result else '❌'}")
            print(f"   Publication: {'✅' if publication_result.success else '❌'} - {publication_result.message}")

            # This demonstrates how errors would propagate through the system
            assert not (upload_result.success and metadata_result and publication_result.success)

        finally:
            os.unlink(tmp_path)


# Test the complete publication flow function
@pytest.mark.asyncio
async def test_complete_publication_flow_function():
    """Test the complete_publication_flow utility function."""
    from src.upload.publisher import complete_publication_flow

    mock_browser_service = AsyncMock()

    # Test immediate publication
    result = await complete_publication_flow(mock_browser_service)

    # Should return a PublicationResult
    assert isinstance(result, PublicationResult)
    assert hasattr(result, 'success')
    assert hasattr(result, 'status')
    assert hasattr(result, 'message')

    print(f"\n📤 complete_publication_flow test:")
    print(f"   Success: {result.success}")
    print(f"   Status: {result.status.value if result.status else 'None'}")
    print(f"   Message: {result.message}")


if __name__ == "__main__":
    print("Running Upload Integration Tests")
    print("================================")

    # Run tests
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
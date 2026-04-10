"""
Video Uploader for Instagram automation.

Handles the complete video upload process to Instagram Reels,
including file selection, upload progress monitoring, and UI automation.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-08
"""

import asyncio
import os
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

from dotenv import load_dotenv

# Load Instagram configuration
load_dotenv('.env.instagram')


class UploadError(Exception):
    """Base error for upload operations."""
    pass


class VideoValidationError(UploadError):
    """Error when video validation fails."""
    pass


class UploadTimeoutError(UploadError):
    """Error when upload times out."""
    pass


class UploadStatus(Enum):
    """Status of upload operation."""
    PENDING = "pending"
    VALIDATING = "validating"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VideoInfo:
    """Information about video to upload."""
    path: Path
    caption: str = ""
    hashtags: List[str] = field(default_factory=list)
    location: Optional[str] = None
    duration_seconds: Optional[float] = None
    size_mb: Optional[float] = None
    format: Optional[str] = None

    def __post_init__(self):
        """Validate video info after initialization."""
        # Convert to Path if string provided
        if isinstance(self.path, str):
            self.path = Path(self.path)

        if not self.path.exists():
            raise VideoValidationError(f"Video file not found: {self.path}")

        # Auto-detect format if not provided
        if not self.format:
            self.format = self.path.suffix.lower().lstrip('.')

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate video file.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check file exists
        if not self.path.exists():
            errors.append(f"File does not exist: {self.path}")
            return False, errors

        # Check file size
        max_size_mb = float(os.getenv('INSTAGRAM_MAX_VIDEO_SIZE_MB', '100'))
        size_mb = self.path.stat().st_size / (1024 * 1024)
        self.size_mb = size_mb

        if size_mb > max_size_mb:
            errors.append(f"Video size {size_mb:.1f}MB exceeds maximum {max_size_mb}MB")

        # Check format
        allowed_formats = os.getenv('INSTAGRAM_ALLOWED_FORMATS', 'mp4,mov').split(',')
        if self.format not in allowed_formats:
            errors.append(f"Format '{self.format}' not allowed. Allowed: {', '.join(allowed_formats)}")

        # Check duration (will be validated during actual upload by Instagram)
        max_duration = int(os.getenv('INSTAGRAM_MAX_VIDEO_DURATION_SEC', '90'))
        if self.duration_seconds and self.duration_seconds > max_duration:
            errors.append(f"Duration {self.duration_seconds}s exceeds maximum {max_duration}s")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'path': str(self.path),
            'caption': self.caption,
            'hashtags': self.hashtags,
            'location': self.location,
            'duration_seconds': self.duration_seconds,
            'size_mb': self.size_mb,
            'format': self.format
        }


@dataclass
class UploadResult:
    """Result of upload operation."""
    success: bool
    video_info: VideoInfo
    status: UploadStatus
    message: str = ""
    upload_id: Optional[str] = None
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VideoUploader:
    """Handles video upload to Instagram Reels."""

    def __init__(self, browser_service=None):
        """Initialize video uploader.

        Args:
            browser_service: Optional BrowserService instance.
                If None, will create its own.
        """
        self.browser_service = browser_service
        self._is_authenticated = False
        self._upload_timeout = int(os.getenv('INSTAGRAM_UPLOAD_TIMEOUT', '300'))  # 5 minutes
        self._max_retries = int(os.getenv('INSTAGRAM_UPLOAD_MAX_RETRIES', '3'))

        # Upload directories from config
        self.input_dir = Path(os.getenv('INSTAGRAM_VIDEO_INPUT_DIR', './videos/to_upload'))
        self.processed_dir = Path(os.getenv('INSTAGRAM_VIDEO_PROCESSED_DIR', './videos/processed'))
        self.failed_dir = Path(os.getenv('INSTAGRAM_VIDEO_FAILED_DIR', './videos/failed'))

        # Create directories if they don't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

    async def ensure_authenticated(self) -> bool:
        """Ensure user is authenticated before upload.

        Returns:
            bool: True if authenticated, False otherwise
        """
        if self._is_authenticated:
            return True

        # If no browser service provided, create one
        if not self.browser_service:
            from src.auth.browser_service import BrowserService, BrowserConfig

            config = BrowserConfig(
                headless=os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true',
                slow_mo=int(os.getenv('PLAYWRIGHT_SLOW_MO', '100'))
            )
            self.browser_service = BrowserService(config)
            await self.browser_service.initialize()

        # Navigate to Instagram and check if logged in
        await self.browser_service.navigate_to_instagram()

        # Check for home icon to verify login
        try:
            await self.browser_service.page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
            self._is_authenticated = True
            print("✅ Already authenticated")
            return True
        except:
            print("❌ Not authenticated. Need to login first.")
            return False

    async def navigate_to_upload(self) -> bool:
        """Navigate to Instagram upload page.

        Returns:
            bool: True if successfully navigated to upload page
        """
        print("📍 Navigating to upload page...")

        if not await self.ensure_authenticated():
            print("❌ Cannot navigate to upload: not authenticated")
            return False

        try:
            # Click create button (plus icon)
            create_button = 'svg[aria-label="New post"]'

            if await self.browser_service.wait_for_element(create_button, timeout=10000):
                await self.browser_service.click_like_human(create_button)
                await asyncio.sleep(2)
                print("✅ Clicked create button")
            else:
                # Alternative selector
                create_button_alt = 'div[role="button"]:has-text("Create")'
                if await self.browser_service.wait_for_element(create_button_alt, timeout=5000):
                    await self.browser_service.click_like_human(create_button_alt)
                    await asyncio.sleep(2)
                    print("✅ Clicked create button (alternative)")
                else:
                    print("❌ Could not find create button")
                    return False

            # Wait for upload modal to appear
            upload_modal = 'div[role="dialog"]'
            if await self.browser_service.wait_for_element(upload_modal, timeout=10000):
                print("✅ Upload modal appeared")
                return True
            else:
                print("❌ Upload modal did not appear")
                return False

        except Exception as e:
            print(f"❌ Error navigating to upload: {e}")
            await self.browser_service.take_screenshot("upload_navigation_error")
            return False

    async def select_video_file(self, video_path: Path) -> bool:
        """Select video file for upload.

        Args:
            video_path: Path to video file

        Returns:
            bool: True if file selected successfully
        """
        print(f"📁 Selecting video file: {video_path}")

        try:
            # Wait for file input element
            file_input = 'input[type="file"][accept*="video"]'

            if not await self.browser_service.wait_for_element(file_input, timeout=10000):
                print("❌ File input not found")
                return False

            # Set the file path
            await self.browser_service.page.set_input_files(file_input, str(video_path))
            await asyncio.sleep(3)  # Wait for file to be processed

            # Check for video preview
            video_preview = 'video, div[data-testid="video-preview"]'
            if await self.browser_service.wait_for_element(video_preview, timeout=10000):
                print("✅ Video file selected and preview loaded")
                return True
            else:
                # Check for error messages
                error_selectors = [
                    'div[role="alert"]',
                    'div:has-text("error")',
                    'div:has-text("unsupported")',
                    'div:has-text("too large")'
                ]

                for selector in error_selectors:
                    if await self.browser_service.is_element_visible(selector, timeout=2000):
                        error_text = await self.browser_service.get_element_text(selector)
                        print(f"❌ Upload error: {error_text}")
                        await self.browser_service.take_screenshot("video_selection_error")
                        return False

                print("❌ Video preview not found (unknown error)")
                await self.browser_service.take_screenshot("video_preview_missing")
                return False

        except Exception as e:
            print(f"❌ Error selecting video file: {e}")
            await self.browser_service.take_screenshot("file_selection_error")
            return False

    async def upload_video(self, video_info: VideoInfo) -> UploadResult:
        """Upload video to Instagram.

        Args:
            video_info: Video information

        Returns:
            UploadResult with upload status
        """
        start_time = time.time()
        result = UploadResult(
            success=False,
            video_info=video_info,
            status=UploadStatus.PENDING,
            message="Starting upload process"
        )

        print(f"🚀 Starting upload process for: {video_info.path.name}")
        size_display = f"{video_info.size_mb:.1f}MB" if video_info.size_mb else "unknown size"
        format_display = video_info.format if video_info.format else "unknown format"
        print(f"   Size: {size_display}, Format: {format_display}")

        # Validate video
        result.status = UploadStatus.VALIDATING
        is_valid, errors = video_info.validate()

        if not is_valid:
            result.status = UploadStatus.FAILED
            result.errors = errors
            result.message = f"Video validation failed: {', '.join(errors)}"
            print(f"❌ {result.message}")
            return result

        print("✅ Video validation passed")

        # Navigate to upload page
        if not await self.navigate_to_upload():
            result.status = UploadStatus.FAILED
            result.message = "Failed to navigate to upload page"
            print(f"❌ {result.message}")
            return result

        print("✅ Navigated to upload page")

        # Select video file
        result.status = UploadStatus.UPLOADING
        if not await self.select_video_file(video_info.path):
            result.status = UploadStatus.FAILED
            result.message = "Failed to select video file"
            print(f"❌ {result.message}")
            return result

        print("✅ Video file selected")

        # Wait for upload to complete
        result.status = UploadStatus.PROCESSING
        print("⏳ Waiting for upload to process...")

        try:
            # Look for next button (indicates upload completed)
            next_button_selectors = [
                'div[role="button"]:has-text("Next")',
                'button:has-text("Next")',
                'div:has-text("Next")'
            ]

            upload_completed = False
            for attempt in range(self._max_retries):
                for selector in next_button_selectors:
                    if await self.browser_service.wait_for_element(selector, timeout=30000):
                        upload_completed = True
                        print(f"✅ Upload completed (attempt {attempt + 1})")
                        break

                if upload_completed:
                    break

                print(f"⏳ Upload still processing... (attempt {attempt + 1}/{self._max_retries})")
                await asyncio.sleep(5)

            if not upload_completed:
                result.status = UploadStatus.FAILED
                result.message = "Upload timed out - next button not found"
                print(f"❌ {result.message}")
                await self.browser_service.take_screenshot("upload_timeout")
                return result

            result.status = UploadStatus.COMPLETED
            result.success = True
            result.message = "Video uploaded successfully, ready for metadata entry"
            print("🎉 Video upload completed successfully!")

            # Get potential upload ID from page
            try:
                # Try to extract any upload ID from the page
                page_url = self.browser_service.page.url
                if "upload_id" in page_url:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(page_url)
                    params = urllib.parse.parse_qs(parsed.query)
                    if 'upload_id' in params:
                        result.upload_id = params['upload_id'][0]
            except:
                pass  # Upload ID not critical

        except Exception as e:
            result.status = UploadStatus.FAILED
            result.message = f"Upload error: {str(e)}"
            print(f"❌ {result.message}")
            await self.browser_service.take_screenshot("upload_exception")

        finally:
            result.duration_seconds = time.time() - start_time
            print(f"⏱️  Upload duration: {result.duration_seconds:.1f}s")

        return result

    async def move_processed_video(self, video_info: VideoInfo, success: bool) -> Path:
        """Move video to processed or failed directory.

        Args:
            video_info: Video information
            success: Whether upload was successful

        Returns:
            Path: New location of video file
        """
        target_dir = self.processed_dir if success else self.failed_dir

        # Create new filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_name = f"{timestamp}_{video_info.path.name}"
        target_path = target_dir / new_name

        try:
            # Copy file (safer than move in case of errors)
            import shutil
            shutil.copy2(video_info.path, target_path)

            # Optionally remove original (uncomment if desired)
            # video_info.path.unlink()

            print(f"📦 Video moved to: {target_path}")
            return target_path

        except Exception as e:
            print(f"⚠️  Could not move video file: {e}")
            return video_info.path

    async def upload_video_with_retry(self, video_info: VideoInfo, max_retries: int = None) -> UploadResult:
        """Upload video with retry logic.

        Args:
            video_info: Video information
            max_retries: Maximum number of retry attempts

        Returns:
            UploadResult with final status
        """
        if max_retries is None:
            max_retries = self._max_retries

        last_result = None

        for attempt in range(max_retries + 1):  # +1 for initial attempt
            print(f"\n🔄 Upload attempt {attempt + 1}/{max_retries + 1}")

            result = await self.upload_video(video_info)
            last_result = result

            if result.success:
                # Move to processed directory
                await self.move_processed_video(video_info, success=True)
                return result
            else:
                print(f"❌ Attempt {attempt + 1} failed: {result.message}")

                if attempt < max_retries:
                    # Wait before retry (exponential backoff)
                    wait_time = min(30, 2 ** attempt)  # 1, 2, 4, 8, 16, 30, 30, ...
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)

                    # Refresh page before retry
                    try:
                        await self.browser_service.reload_page()
                    except:
                        pass

        # All attempts failed
        print(f"💀 All {max_retries + 1} upload attempts failed")

        # Move to failed directory
        await self.move_processed_video(video_info, success=False)

        return last_result

    async def close(self):
        """Close browser service if owned by this uploader."""
        if self.browser_service and not self._is_authenticated:
            await self.browser_service.close()


# Utility functions
async def upload_single_video(video_path: str | Path, caption: str = "",
                             hashtags: List[str] = None, location: str = None) -> UploadResult:
    """Convenience function to upload a single video.

    Args:
        video_path: Path to video file
        caption: Video caption
        hashtags: List of hashtags
        location: Location tag

    Returns:
        UploadResult with upload status
    """
    uploader = None

    try:
        # Create video info
        video_info = VideoInfo(
            path=Path(video_path),
            caption=caption,
            hashtags=hashtags or [],
            location=location
        )

        # Create uploader
        uploader = VideoUploader()

        # Upload with retry
        result = await uploader.upload_video_with_retry(video_info)

        return result

    except Exception as e:
        return UploadResult(
            success=False,
            video_info=None,
            status=UploadStatus.FAILED,
            message=f"Upload failed: {str(e)}",
            errors=[str(e)]
        )

    finally:
        if uploader:
            await uploader.close()


# Example usage
async def example_usage():
    """Example usage of VideoUploader."""
    print("VideoUploader Example Usage")
    print("==========================")

    # Create a test video info (using a placeholder path)
    test_video_path = Path("./example_video.mp4")

    # Check if test file exists, create dummy if not
    if not test_video_path.exists():
        print(f"⚠️  Test video not found: {test_video_path}")
        print("   Creating dummy file for example...")
        test_video_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_video_path, 'wb') as f:
            f.write(b'dummy video content')

    video_info = VideoInfo(
        path=test_video_path,
        caption="Amazing sunset at the beach! 🌅",
        hashtags=["#sunset", "#beach", "#nature", "#photography"],
        location="Santa Monica Beach"
    )

    # Validate
    is_valid, errors = video_info.validate()
    print(f"\n1. Video Validation: {'✅' if is_valid else '❌'}")
    if errors:
        print(f"   Errors: {', '.join(errors)}")
    else:
        print(f"   Size: {video_info.size_mb:.1f}MB, Format: {video_info.format}")

    print("\n2. Upload Process Simulation:")
    print("   • Navigate to Instagram")
    print("   • Click create button")
    print("   • Select video file")
    print("   • Wait for upload")
    print("   • Handle metadata (next step)")

    print("\n🎉 Example completed (simulation mode)")
    print("   Note: Actual upload requires real video file and authentication")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
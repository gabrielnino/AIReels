"""
Playwright uploader for Instagram.

This module provides a real implementation of InstagramUploader
using Playwright UI automation (browser automation).

Created by: Sam Lead Developer
Date: 2026-04-11
"""

import asyncio
import os
import time
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .data_models import VideoMetadata, UploadResult, UploadStatus, UploadOptions
from .pipeline_bridge import InstagramUploader


class PlaywrightUploader(InstagramUploader):
    """
    Instagram uploader using Playwright UI automation.

    This uploader automates the Instagram web interface to upload videos as Reels.
    It uses the existing instagram-upload codebase as foundation.
    """

    def __init__(
        self,
        headless: bool = False,
        slow_mo: int = 100,
        timeout_seconds: int = 300,
        max_retries: int = 3,
        screenshots_dir: str = "./logs/screenshots"
    ):
        """
        Initialize the Playwright uploader.

        Args:
            headless: Whether to run browser in headless mode
            slow_mo: Delay between actions in milliseconds
            timeout_seconds: Timeout for operations
            max_retries: Maximum retry attempts
            screenshots_dir: Directory for debug screenshots
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.screenshots_dir = Path(screenshots_dir)

        # Import instagram-upload components
        try:
            # Add instagram-upload to path
            import sys
            instagram_upload_path = Path(__file__).parent.parent.parent / "instagram-upload"
            sys.path.insert(0, str(instagram_upload_path))

            from src.upload.video_uploader import VideoUploader, VideoInfo
            from src.auth.browser_service import BrowserService, BrowserConfig

            self.VideoUploader = VideoUploader
            self.VideoInfo = VideoInfo
            self.BrowserService = BrowserService
            self.BrowserConfig = BrowserConfig

            self.logger = logging.getLogger(__name__)
            self.logger.info("PlaywrightUploader initialized with instagram-upload integration")

        except ImportError as e:
            self.logger = logging.getLogger(__name__)
            self.logger.error(f"Failed to import instagram-upload modules: {e}")
            raise RuntimeError(
                "Cannot initialize PlaywrightUploader: instagram-upload module not available. "
                "Make sure the instagram-upload directory exists and has the required modules."
            )

        # Browser and uploader instances
        self.browser_service = None
        self.video_uploader = None
        self.is_authenticated = False

    async def upload_video(
        self,
        metadata: VideoMetadata,
        options: Optional[UploadOptions] = None
    ) -> UploadResult:
        """
        Upload a video to Instagram using Playwright UI automation.

        Args:
            metadata: Video metadata
            options: Upload options

        Returns:
            UploadResult with status and identifiers
        """
        start_time = datetime.now()
        upload_options = options or UploadOptions()

        try:
            self.logger.info(f"Starting Playwright upload: {metadata.video_path}")

            # Step 1: Initialize browser and uploader
            await self._initialize_uploader()

            # Step 2: Convert VideoMetadata to VideoInfo
            video_info = self._convert_to_video_info(metadata)

            # Step 3: Upload video with retry logic
            self.logger.info("Uploading video with retry logic")
            instagram_result = await self.video_uploader.upload_video_with_retry(
                video_info,
                max_retries=self.max_retries
            )

            # Step 4: Convert to our UploadResult format
            result = self._convert_upload_result(
                instagram_result, start_time, metadata, upload_options
            )

            self.logger.info(f"Upload completed with status: {result.status.value}")
            return result

        except Exception as e:
            error_msg = f"Playwright upload failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            # Take screenshot for debugging
            await self._take_debug_screenshot("upload_failure")

            return self._create_error_result(
                error_msg, start_time, metadata, upload_options
            )

    async def validate_credentials(self) -> bool:
        """
        Validate that the uploader can authenticate with Instagram.

        Returns:
            True if authentication is possible, False otherwise
        """
        try:
            await self._initialize_uploader()

            # Check if already authenticated via browser service
            if hasattr(self.video_uploader, '_is_authenticated'):
                if self.video_uploader._is_authenticated:
                    self.logger.info("Already authenticated via video uploader")
                    self.is_authenticated = True
                    return True

            # Try to authenticate using the video uploader's method
            if hasattr(self.video_uploader, 'ensure_authenticated'):
                authenticated = await self.video_uploader.ensure_authenticated()
                if authenticated:
                    self.logger.info("Authentication successful via ensure_authenticated")
                    self.is_authenticated = True
                    return True

            # Fallback: check if we can navigate to Instagram home
            self.logger.info("Attempting to navigate to Instagram to check authentication")
            await self.browser_service.navigate_to_instagram()

            # Check for home icon (indicates logged in)
            try:
                await self.browser_service.page.wait_for_selector(
                    'svg[aria-label="Home"]',
                    timeout=5000
                )
                self.logger.info("Authentication confirmed via home icon")
                self.is_authenticated = True
                return True
            except:
                self.logger.warning("Not authenticated - home icon not found")
                return False

        except Exception as e:
            self.logger.error(f"Authentication validation failed: {str(e)}")
            return False

    def get_uploader_info(self) -> Dict[str, Any]:
        """Get information about this uploader implementation."""
        return {
            "type": "playwright_ui",
            "name": "PlaywrightUploader",
            "version": "0.1.0",
            "configuration": {
                "headless": self.headless,
                "slow_mo": self.slow_mo,
                "timeout_seconds": self.timeout_seconds,
                "max_retries": self.max_retries,
                "screenshots_dir": str(self.screenshots_dir),
            },
            "capabilities": {
                "actual_upload": True,
                "ui_automation": True,
                "supports_reels": True,
                "requires_access_token": False,
                "supports_scheduled_posts": False,
                "browser_based": True,
            },
            "status": {
                "initialized": self.browser_service is not None,
                "authenticated": self.is_authenticated,
            }
        }

    async def _initialize_uploader(self):
        """Initialize browser service and video uploader."""
        if self.browser_service is not None and self.video_uploader is not None:
            return

        self.logger.info("Initializing browser service and video uploader")

        # Create browser configuration
        config = self.BrowserConfig(
            headless=self.headless,
            slow_mo=self.slow_mo
        )

        # Initialize browser service
        self.browser_service = self.BrowserService(config)
        await self.browser_service.initialize()

        # Create video uploader with the browser service
        self.video_uploader = self.VideoUploader(self.browser_service)

        self.logger.info("Browser service and video uploader initialized")

    def _convert_to_video_info(self, metadata: VideoMetadata):
        """Convert VideoMetadata to instagram-upload's VideoInfo."""
        return self.VideoInfo(
            path=Path(metadata.video_path),
            caption=metadata.caption or "",
            hashtags=metadata.hashtags or [],
            location=metadata.location,
            duration_seconds=metadata.duration_seconds,
            size_mb=metadata.file_size_mb,
            format=metadata.video_format
        )

    def _convert_upload_result(
        self,
        instagram_result,
        start_time: datetime,
        metadata: VideoMetadata,
        options: UploadOptions
    ) -> UploadResult:
        """Convert instagram-upload result to our UploadResult format."""
        # Map statuses
        status_map = {
            "pending": UploadStatus.PENDING,
            "validating": UploadStatus.VALIDATING,
            "uploading": UploadStatus.UPLOADING,
            "processing": UploadStatus.PROCESSING,
            "completed": UploadStatus.COMPLETED,
            "failed": UploadStatus.FAILED,
        }

        result_status = status_map.get(
            instagram_result.status.value if hasattr(instagram_result.status, 'value')
            else str(instagram_result.status).lower(),
            UploadStatus.FAILED
        )

        total_duration = (datetime.now() - start_time).total_seconds()

        return UploadResult(
            status=result_status,
            upload_id=instagram_result.upload_id,
            media_id=instagram_result.upload_id,  # Instagram doesn't give media ID immediately
            error_message=instagram_result.message if not instagram_result.success else None,
            retry_count=getattr(instagram_result, 'retry_count', 0),
            upload_duration_seconds=instagram_result.duration_seconds,
            total_duration_seconds=total_duration,
            metadata={
                "upload_type": "playwright_ui",
                "video_path": metadata.video_path,
                "success": instagram_result.success,
                "errors": instagram_result.errors if hasattr(instagram_result, 'errors') else [],
                "options": options.to_dict(),
            }
        )

    async def _take_debug_screenshot(self, name: str):
        """Take a debug screenshot."""
        try:
            if self.browser_service and hasattr(self.browser_service, 'take_screenshot'):
                await self.browser_service.take_screenshot(name)
            elif self.browser_service and hasattr(self.browser_service, 'page'):
                self.screenshots_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = self.screenshots_dir / f"{name}_{int(time.time())}.png"
                await self.browser_service.page.screenshot(path=str(screenshot_path))
                self.logger.info(f"Debug screenshot saved: {screenshot_path}")
        except Exception as e:
            self.logger.warning(f"Could not take screenshot: {e}")

    def _create_error_result(
        self,
        error_message: str,
        start_time: datetime,
        metadata: VideoMetadata,
        options: UploadOptions
    ) -> UploadResult:
        """Create an error result."""
        total_duration = (datetime.now() - start_time).total_seconds()

        return UploadResult(
            status=UploadStatus.FAILED,
            error_message=error_message,
            total_duration_seconds=total_duration,
            metadata={
                "upload_type": "playwright_ui",
                "error_time": datetime.now().isoformat(),
                "video_path": metadata.video_path,
                "options": options.to_dict(),
            }
        )

    async def close(self):
        """Clean up resources."""
        if self.video_uploader:
            try:
                await self.video_uploader.close()
                self.logger.info("Video uploader closed")
            except Exception as e:
                self.logger.warning(f"Error closing video uploader: {e}")

        if self.browser_service:
            try:
                await self.browser_service.close()
                self.logger.info("Browser service closed")
            except Exception as e:
                self.logger.warning(f"Error closing browser service: {e}")

        self.browser_service = None
        self.video_uploader = None
        self.is_authenticated = False


# Factory function for convenience
async def create_playwright_uploader(
    headless: bool = False,
    **kwargs
) -> PlaywrightUploader:
    """
    Create and initialize a PlaywrightUploader instance.

    Args:
        headless: Whether to run browser in headless mode
        **kwargs: Additional arguments for PlaywrightUploader

    Returns:
        Initialized PlaywrightUploader instance
    """
    uploader = PlaywrightUploader(headless=headless, **kwargs)

    # Test initialization
    try:
        # This will import the required modules
        import sys
        instagram_upload_path = Path(__file__).parent.parent.parent / "instagram-upload"
        sys.path.insert(0, str(instagram_upload_path))

        # Test import
        import src.upload.video_uploader
        import src.auth.browser_service

        return uploader
    except ImportError as e:
        raise RuntimeError(
            f"Cannot create PlaywrightUploader: instagram-upload modules not available. "
            f"Error: {e}\n"
            f"Make sure instagram-upload directory exists at: {instagram_upload_path}"
        )
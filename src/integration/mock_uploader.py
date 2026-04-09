"""
Mock Instagram uploader for testing and development.

This module provides a mock implementation of InstagramUploader
that simulates upload behavior without actually calling any API
or browser automation. Useful for testing the pipeline bridge
while the actual uploader implementation is being decided/developed.

Created by: Sam Lead Developer
Date: 2026-04-08
"""

import asyncio
import logging
import random
import time
from typing import Optional, Dict, Any
from datetime import datetime

from .data_models import VideoMetadata, UploadResult, UploadStatus, UploadOptions
from .pipeline_bridge import InstagramUploader


class MockInstagramUploader(InstagramUploader):
    """
    Mock uploader that simulates Instagram upload behavior.

    This uploader doesn't actually upload anything but simulates
    the behavior for testing purposes. It can be configured to
    succeed, fail, or behave randomly.
    """

    def __init__(
        self,
        success_rate: float = 0.8,
        average_delay_seconds: float = 5.0,
        delay_variation: float = 2.0,
        simulate_validation: bool = True
    ):
        """
        Initialize the mock uploader.

        Args:
            success_rate: Probability of successful upload (0.0 to 1.0)
            average_delay_seconds: Average delay to simulate upload time
            delay_variation: Maximum variation in delay (± this value)
            simulate_validation: Whether to simulate credential validation
        """
        self.success_rate = max(0.0, min(1.0, success_rate))
        self.average_delay = max(0.1, average_delay_seconds)
        self.delay_variation = max(0.0, delay_variation)
        self.simulate_validation = simulate_validation
        self.logger = logging.getLogger(__name__)

        # Statistics
        self.upload_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_delay = 0.0

    async def upload_video(
        self,
        metadata: VideoMetadata,
        options: Optional[UploadOptions] = None
    ) -> UploadResult:
        """
        Simulate uploading a video to Instagram.

        Args:
            metadata: Video metadata
            options: Upload options

        Returns:
            UploadResult with simulated outcome
        """
        self.upload_count += 1
        upload_start = datetime.now()

        # Log start
        self.logger.info(f"Mock upload starting for: {metadata.video_path}")

        # Simulate upload delay
        delay = self._calculate_delay()
        self.total_delay += delay
        self.logger.debug(f"Simulating upload delay: {delay:.1f}s")
        await asyncio.sleep(delay)

        # Determine success/failure
        is_successful = random.random() < self.success_rate
        upload_end = datetime.now()

        if is_successful:
            self.success_count += 1
            return self._create_success_result(metadata, upload_start, upload_end, options)
        else:
            self.failure_count += 1
            return self._create_failure_result(metadata, upload_start, upload_end, options)

    async def validate_credentials(self) -> bool:
        """
        Simulate credential validation.

        Returns:
            True if simulating successful validation
        """
        if not self.simulate_validation:
            return True

        # Simulate validation delay
        await asyncio.sleep(0.5)

        # 95% chance of valid credentials
        is_valid = random.random() < 0.95

        if is_valid:
            self.logger.debug("Mock credentials validation: SUCCESS")
        else:
            self.logger.warning("Mock credentials validation: FAILED")

        return is_valid

    def get_uploader_info(self) -> Dict[str, Any]:
        """Get information about this mock uploader."""
        return {
            "type": "mock",
            "name": "MockInstagramUploader",
            "version": "0.1.0",
            "configuration": {
                "success_rate": self.success_rate,
                "average_delay_seconds": self.average_delay,
                "delay_variation": self.delay_variation,
                "simulate_validation": self.simulate_validation,
            },
            "statistics": {
                "total_uploads": self.upload_count,
                "successful_uploads": self.success_count,
                "failed_uploads": self.failure_count,
                "success_rate": self.success_count / self.upload_count if self.upload_count > 0 else 0.0,
                "average_delay": self.total_delay / self.upload_count if self.upload_count > 0 else 0.0,
            },
            "capabilities": {
                "actual_upload": False,
                "simulation": True,
                "configurable_success_rate": True,
                "configurable_delay": True,
            }
        }

    def _calculate_delay(self) -> float:
        """Calculate random delay for simulation."""
        base_delay = self.average_delay
        variation = random.uniform(-self.delay_variation, self.delay_variation)
        return max(0.1, base_delay + variation)

    def _create_success_result(
        self,
        metadata: VideoMetadata,
        start_time: datetime,
        end_time: datetime,
        options: Optional[UploadOptions]
    ) -> UploadResult:
        """Create a successful upload result."""
        upload_duration = (end_time - start_time).total_seconds()

        # Generate mock media ID
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        media_id = f"mock_media_{timestamp}_{random_suffix}"

        return UploadResult(
            status=UploadStatus.COMPLETED,
            upload_id=f"mock_upload_{timestamp}",
            media_id=media_id,
            publish_time=end_time,
            upload_duration_seconds=upload_duration,
            total_duration_seconds=upload_duration,
            metadata={
                "simulated": True,
                "video_path": metadata.video_path,
                "caption_length": len(metadata.caption),
                "hashtag_count": len(metadata.hashtags),
                "mock_upload": True,
            }
        )

    def _create_failure_result(
        self,
        metadata: VideoMetadata,
        start_time: datetime,
        end_time: datetime,
        options: Optional[UploadOptions]
    ) -> UploadResult:
        """Create a failed upload result."""
        upload_duration = (end_time - start_time).total_seconds()

        # Random failure reasons
        failure_reasons = [
            "Network timeout during upload",
            "Instagram API rate limit exceeded",
            "Video format not supported",
            "Caption contains blocked content",
            "Temporary service outage",
            "Authentication token expired",
            "File size exceeds limit",
            "Upload session expired",
        ]

        error_message = random.choice(failure_reasons)

        return UploadResult(
            status=UploadStatus.FAILED,
            error_message=error_message,
            upload_duration_seconds=upload_duration,
            total_duration_seconds=upload_duration,
            metadata={
                "simulated": True,
                "video_path": metadata.video_path,
                "failure_reason": error_message,
                "mock_upload": True,
            }
        )

    def reset_statistics(self) -> None:
        """Reset upload statistics."""
        self.upload_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_delay = 0.0
        self.logger.info("Mock uploader statistics reset")

    def set_success_rate(self, rate: float) -> None:
        """Set the success rate for future uploads."""
        self.success_rate = max(0.0, min(1.0, rate))
        self.logger.info(f"Mock uploader success rate set to: {self.success_rate}")

    def set_delay_parameters(
        self,
        average_delay: float,
        variation: float
    ) -> None:
        """Set delay parameters for simulation."""
        self.average_delay = max(0.1, average_delay)
        self.delay_variation = max(0.0, variation)
        self.logger.info(
            f"Mock uploader delay set to: {self.average_delay}s ± {self.delay_variation}s"
        )


class AlwaysSuccessUploader(MockInstagramUploader):
    """Mock uploader that always succeeds."""

    def __init__(self, delay_seconds: float = 3.0):
        super().__init__(
            success_rate=1.0,
            average_delay_seconds=delay_seconds,
            delay_variation=1.0,
            simulate_validation=True
        )

    async def upload_video(self, metadata, options=None):
        # Override to ensure always success
        self.upload_count += 1
        upload_start = datetime.now()

        delay = self._calculate_delay()
        await asyncio.sleep(delay)

        self.success_count += 1
        upload_end = datetime.now()

        return self._create_success_result(metadata, upload_start, upload_end, options)


class AlwaysFailureUploader(MockInstagramUploader):
    """Mock uploader that always fails."""

    def __init__(self, delay_seconds: float = 2.0):
        super().__init__(
            success_rate=0.0,
            average_delay_seconds=delay_seconds,
            delay_variation=0.5,
            simulate_validation=True
        )

    async def upload_video(self, metadata, options=None):
        # Override to ensure always failure
        self.upload_count += 1
        upload_start = datetime.now()

        delay = self._calculate_delay()
        await asyncio.sleep(delay)

        self.failure_count += 1
        upload_end = datetime.now()

        return self._create_failure_result(metadata, upload_start, upload_end, options)


class FlakyUploader(MockInstagramUploader):
    """Mock uploader with configurable flaky behavior."""

    def __init__(
        self,
        initial_success: bool = True,
        failure_after_successes: int = 3,
        recovery_after_failures: int = 2,
        delay_seconds: float = 4.0
    ):
        super().__init__(
            success_rate=0.5,  # Will be overridden by behavior
            average_delay_seconds=delay_seconds,
            delay_variation=1.0,
            simulate_validation=True
        )
        self.initial_success = initial_success
        self.failure_after_successes = failure_after_successes
        self.recovery_after_failures = recovery_after_failures
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        self.currently_succeeding = initial_success

    async def upload_video(self, metadata, options=None):
        # Determine success based on pattern
        if self.currently_succeeding:
            self.consecutive_successes += 1
            self.consecutive_failures = 0

            if self.consecutive_successes >= self.failure_after_successes:
                self.currently_succeeding = False
                self.consecutive_successes = 0
                self.logger.warning("Flaky uploader: Switching to failure mode")
        else:
            self.consecutive_failures += 1
            self.consecutive_successes = 0

            if self.consecutive_failures >= self.recovery_after_failures:
                self.currently_succeeding = True
                self.consecutive_failures = 0
                self.logger.info("Flaky uploader: Switching to success mode")

        # Call parent with current success state
        original_rate = self.success_rate
        self.success_rate = 1.0 if self.currently_succeeding else 0.0

        try:
            return await super().upload_video(metadata, options)
        finally:
            self.success_rate = original_rate
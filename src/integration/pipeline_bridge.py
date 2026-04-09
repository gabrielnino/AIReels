"""
Pipeline bridge for connecting generation pipeline with upload system.

This module provides an abstract bridge that can work with any
Instagram uploader implementation (Graph API or Playwright UI).

Created by: Sam Lead Developer
Date: 2026-04-08
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from .data_models import VideoMetadata, UploadResult, UploadStatus, UploadOptions
from .metadata_adapter import adapt_qwen_to_upload, validate_metadata, enrich_metadata_with_ai


class InstagramUploader(ABC):
    """
    Abstract base class for Instagram uploaders.

    This interface defines the contract that any Instagram uploader
    must implement, whether it uses Graph API or Playwright UI.
    """

    @abstractmethod
    async def upload_video(
        self,
        metadata: VideoMetadata,
        options: Optional[UploadOptions] = None
    ) -> UploadResult:
        """
        Upload a video to Instagram.

        Args:
            metadata: Video metadata including path and caption
            options: Upload configuration options

        Returns:
            UploadResult with status and identifiers
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that the uploader has valid credentials/session.

        Returns:
            True if credentials are valid, False otherwise
        """
        pass

    @abstractmethod
    def get_uploader_info(self) -> Dict[str, Any]:
        """
        Get information about this uploader implementation.

        Returns:
            Dictionary with uploader name, type, capabilities, etc.
        """
        pass


class PipelineBridge:
    """
    Bridge between qwen-poc generation pipeline and Instagram uploader.

    This class handles the complete flow from qwen-poc output to
    Instagram upload, including metadata adaptation, validation,
    and upload execution.
    """

    def __init__(
        self,
        uploader: InstagramUploader,
        options: Optional[UploadOptions] = None
    ):
        """
        Initialize the pipeline bridge.

        Args:
            uploader: InstagramUploader implementation to use
            options: Default upload options
        """
        self.uploader = uploader
        self.default_options = options or UploadOptions()
        self.logger = logging.getLogger(__name__)

    async def process_and_upload(
        self,
        qwen_output: Dict[str, Any],
        options: Optional[UploadOptions] = None,
        enrich_with_ai: bool = False
    ) -> UploadResult:
        """
        Process qwen-poc output and upload to Instagram.

        This is the main method that orchestrates the complete flow:
        1. Adapt qwen-poc output to VideoMetadata
        2. Optionally enrich metadata with AI
        3. Validate metadata and video
        4. Upload to Instagram using the configured uploader
        5. Return detailed upload result

        Args:
            qwen_output: Dictionary from qwen-poc's run_content_engine
            options: Upload options (overrides default)
            enrich_with_ai: Whether to enrich metadata with AI

        Returns:
            UploadResult with complete upload information
        """
        start_time = datetime.now()
        upload_options = options or self.default_options

        try:
            # Step 1: Log start
            self.logger.info("Starting pipeline bridge processing")
            self.logger.debug(f"Qwen output keys: {list(qwen_output.keys())}")

            # Step 2: Adapt metadata
            self.logger.info("Adapting qwen-poc output to VideoMetadata")
            metadata = adapt_qwen_to_upload(qwen_output, upload_options)

            # Step 3: Optionally enrich with AI
            if enrich_with_ai:
                self.logger.info("Enriching metadata with AI")
                context = {"source": "qwen-poc", "enrichment_level": "basic"}
                metadata = enrich_metadata_with_ai(metadata, context)

            # Step 4: Log metadata summary
            self._log_metadata_summary(metadata)

            # Step 5: Validate uploader credentials
            self.logger.info("Validating uploader credentials")
            if not await self.uploader.validate_credentials():
                error_msg = "Uploader credentials validation failed"
                self.logger.error(error_msg)
                return self._create_error_result(
                    error_msg, start_time, metadata, upload_options
                )

            # Step 6: Upload video
            self.logger.info("Starting Instagram upload")
            upload_start = datetime.now()
            result = await self.uploader.upload_video(metadata, upload_options)
            upload_end = datetime.now()

            # Step 7: Add timing information
            result.upload_duration_seconds = (upload_end - upload_start).total_seconds()
            result.total_duration_seconds = (datetime.now() - start_time).total_seconds()

            # Step 8: Log result
            self._log_upload_result(result, metadata)

            return result

        except FileNotFoundError as e:
            error_msg = f"Video file not found: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(
                error_msg, start_time, qwen_output, upload_options
            )

        except ValueError as e:
            error_msg = f"Metadata validation failed: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(
                error_msg, start_time, qwen_output, upload_options
            )

        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self._create_error_result(
                error_msg, start_time, qwen_output, upload_options
            )

    async def process_and_upload_with_retry(
        self,
        qwen_output: Dict[str, Any],
        options: Optional[UploadOptions] = None,
        enrich_with_ai: bool = False
    ) -> UploadResult:
        """
        Process and upload with automatic retry logic.

        Args:
            qwen_output: Dictionary from qwen-poc's run_content_engine
            options: Upload options (overrides default)
            enrich_with_ai: Whether to enrich metadata with AI

        Returns:
            UploadResult after retries
        """
        upload_options = options or self.default_options
        max_retries = upload_options.max_retries
        retry_delay = upload_options.retry_delay_seconds

        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                self.logger.info(f"Upload attempt {attempt + 1}/{max_retries + 1}")

                result = await self.process_and_upload(
                    qwen_output, upload_options, enrich_with_ai
                )

                if result.successful:
                    self.logger.info(f"Upload successful on attempt {attempt + 1}")
                    return result
                elif attempt < max_retries:
                    self.logger.warning(
                        f"Upload failed, retrying in {retry_delay} seconds. "
                        f"Error: {result.error_message}"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    self.logger.error(
                        f"Upload failed after {max_retries + 1} attempts. "
                        f"Final error: {result.error_message}"
                    )
                    return result

            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(
                        f"Exception during upload attempt {attempt + 1}, "
                        f"retrying in {retry_delay} seconds: {str(e)}"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    error_msg = f"Failed after {max_retries + 1} attempts: {str(e)}"
                    self.logger.error(error_msg)
                    return self._create_error_result(
                        error_msg, datetime.now(), qwen_output, upload_options
                    )

        # This should never be reached, but just in case
        error_msg = "Unexpected exit from retry loop"
        self.logger.error(error_msg)
        return self._create_error_result(
            error_msg, datetime.now(), qwen_output, upload_options
        )

    def _log_metadata_summary(self, metadata: VideoMetadata) -> None:
        """Log summary of video metadata."""
        summary = {
            "video_path": metadata.video_path,
            "caption_preview": metadata.caption[:100] + "..." if len(metadata.caption) > 100 else metadata.caption,
            "hashtag_count": len(metadata.hashtags),
            "file_size_mb": metadata.file_size_mb,
            "topic": metadata.topic,
            "emotion": metadata.emotion,
        }
        self.logger.info(f"Video metadata: {summary}")

    def _log_upload_result(self, result: UploadResult, metadata: VideoMetadata) -> None:
        """Log upload result."""
        if result.successful:
            self.logger.info(
                f"Upload completed successfully. "
                f"Media ID: {result.media_id}, "
                f"Duration: {result.total_duration_seconds:.1f}s"
            )
        else:
            self.logger.error(
                f"Upload failed. Status: {result.status.value}, "
                f"Error: {result.error_message}"
            )

    def _create_error_result(
        self,
        error_message: str,
        start_time: datetime,
        qwen_output: Dict[str, Any],
        options: UploadOptions
    ) -> UploadResult:
        """Create an error result."""
        total_duration = (datetime.now() - start_time).total_seconds()

        return UploadResult(
            status=UploadStatus.FAILED,
            error_message=error_message,
            total_duration_seconds=total_duration,
            metadata={
                "qwen_output_keys": list(qwen_output.keys()),
                "error_time": datetime.now().isoformat(),
                "options": options.to_dict(),
            }
        )

    def get_bridge_info(self) -> Dict[str, Any]:
        """Get information about this bridge configuration."""
        uploader_info = self.uploader.get_uploader_info()

        return {
            "bridge_version": "0.1.0",
            "uploader": uploader_info,
            "default_options": self.default_options.to_dict(),
            "capabilities": {
                "metadata_adaptation": True,
                "metadata_validation": True,
                "retry_support": True,
                "ai_enrichment": True,
            }
        }
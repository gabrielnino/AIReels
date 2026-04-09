"""
Integration module for connecting qwen-poc generation pipeline with instagram-upload.

This module provides adapters, bridges, and common interfaces to integrate
the video generation system with the upload automation system.

Created by: Sam Lead Developer
Date: 2026-04-08
"""

from .data_models import VideoMetadata, UploadResult, UploadStatus, UploadOptions
from .metadata_adapter import adapt_qwen_to_upload, validate_metadata, enrich_metadata_with_ai, merge_metadata_sources
from .pipeline_bridge import PipelineBridge, InstagramUploader
from .mock_uploader import MockInstagramUploader, AlwaysSuccessUploader, AlwaysFailureUploader, FlakyUploader

__all__ = [
    # Data models
    "VideoMetadata",
    "UploadResult",
    "UploadStatus",
    "UploadOptions",

    # Metadata adapter
    "adapt_qwen_to_upload",
    "validate_metadata",
    "enrich_metadata_with_ai",
    "merge_metadata_sources",

    # Pipeline bridge
    "PipelineBridge",
    "InstagramUploader",

    # Mock uploaders (for testing)
    "MockInstagramUploader",
    "AlwaysSuccessUploader",
    "AlwaysFailureUploader",
    "FlakyUploader",
]

__version__ = "0.1.0"
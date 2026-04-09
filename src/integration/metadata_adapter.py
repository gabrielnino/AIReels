"""
Metadata adapter for converting between qwen-poc output format and VideoMetadata.

This module handles the transformation of data from the generation pipeline
to the standardized format required by the upload system.

Created by: Sam Lead Developer
Date: 2026-04-08
"""

import os
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .data_models import VideoMetadata, UploadOptions


def adapt_qwen_to_upload(
    qwen_output: Dict[str, Any],
    options: Optional[UploadOptions] = None
) -> VideoMetadata:
    """
    Convert qwen-poc pipeline output to VideoMetadata.

    Args:
        qwen_output: Dictionary from qwen-poc's run_content_engine
        options: Optional upload configuration

    Returns:
        VideoMetadata instance ready for upload

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Validate required fields
    required_fields = ["final_video_path"]
    for field in required_fields:
        if field not in qwen_output:
            raise ValueError(f"Missing required field in qwen output: {field}")

    # Get video path and validate it exists
    video_path = qwen_output["final_video_path"]
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Extract and process caption
    caption = qwen_output.get("caption", "")
    if not caption and qwen_output.get("topic"):
        # Generate basic caption from topic if none provided
        caption = f"{qwen_output['topic']} #shorts #reels"

    # Extract hashtags
    hashtags = qwen_output.get("hashtags", [])
    if not hashtags and qwen_output.get("topic"):
        # Generate basic hashtags from topic
        topic = qwen_output["topic"]
        hashtags = _generate_hashtags_from_topic(topic)

    # Extract location if available in metadata
    location = None
    if "location" in qwen_output:
        location = qwen_output["location"]

    # Schedule time (default: now + 1 hour for safety)
    schedule_time = datetime.now() + timedelta(hours=1)

    # Get video file info if possible
    duration_seconds = None
    file_size_mb = None
    video_format = None

    try:
        if os.path.exists(video_path):
            # Get file size
            file_size_bytes = os.path.getsize(video_path)
            file_size_mb = file_size_bytes / (1024 * 1024)

            # Determine format from extension
            _, ext = os.path.splitext(video_path)
            if ext:
                video_format = ext.lower().lstrip('.')
    except (OSError, AttributeError):
        # File info is optional, continue without it
        pass

    # Create VideoMetadata instance
    metadata = VideoMetadata(
        video_path=video_path,
        caption=caption,
        hashtags=hashtags,
        location=location,
        schedule_time=schedule_time,
        topic=qwen_output.get("topic"),
        emotion=qwen_output.get("emotion"),
        cta=qwen_output.get("cta"),
        on_screen_text=qwen_output.get("on_screen_text"),
        duration_seconds=duration_seconds,
        file_size_mb=file_size_mb,
        video_format=video_format,
        is_public=True,
        allow_comments=True,
        allow_embedding=True,
    )

    # Validate the metadata if options require it
    if options and options.validate_metadata:
        validate_metadata(metadata, options)

    return metadata


def validate_metadata(metadata: VideoMetadata, options: UploadOptions) -> None:
    """
    Validate video metadata against Instagram requirements and configuration.

    Args:
        metadata: VideoMetadata to validate
        options: UploadOptions with validation settings

    Raises:
        ValueError: If metadata fails validation
    """
    errors = []

    # Validate video path exists
    if not os.path.exists(metadata.video_path):
        errors.append(f"Video file not found: {metadata.video_path}")

    # Validate file size if known (Instagram limit: ~100MB for Reels)
    if metadata.file_size_mb and metadata.file_size_mb > 100:
        errors.append(f"Video file too large: {metadata.file_size_mb:.1f}MB > 100MB limit")

    # Validate caption length (Instagram limit: 2200 characters)
    if len(metadata.caption) > 2200:
        errors.append(f"Caption too long: {len(metadata.caption)} characters > 2200 limit")

    # Validate hashtags count (Instagram limit: 30 hashtags)
    if len(metadata.hashtags) > 30:
        errors.append(f"Too many hashtags: {len(metadata.hashtags)} > 30 limit")

    # Validate individual hashtags
    for i, tag in enumerate(metadata.hashtags):
        if not tag.startswith("#"):
            errors.append(f"Hashtag {i+1} doesn't start with #: '{tag}'")
        elif len(tag) > 30:  # Instagram hashtag character limit
            errors.append(f"Hashtag {i+1} too long: '{tag}' ({len(tag)} characters)")

    # Validate video format if known
    if metadata.video_format and metadata.video_format.lower() not in ["mp4", "mov", "avi"]:
        errors.append(f"Unsupported video format: {metadata.video_format}")

    if errors:
        error_msg = "Metadata validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)


def _generate_hashtags_from_topic(topic: str) -> List[str]:
    """
    Generate relevant hashtags from a topic.

    Args:
        topic: Topic string

    Returns:
        List of hashtags
    """
    hashtags = []

    # Clean and process topic
    clean_topic = topic.lower().strip()
    words = re.findall(r'\b\w+\b', clean_topic)

    # Add topic-based hashtags
    if words:
        # Use main words as hashtags
        for word in words[:3]:  # Max 3 words from topic
            if len(word) > 2:  # Skip very short words
                hashtags.append(f"#{word}")

    # Add general Reels hashtags
    general_hashtags = [
        "#reels",
        "#shorts",
        "#viral",
        "#fyp",
        "#trending",
        "#instagramreels",
    ]

    # Combine and limit to 15 total
    all_hashtags = hashtags + general_hashtags
    return all_hashtags[:15]


def enrich_metadata_with_ai(
    metadata: VideoMetadata,
    context: Optional[Dict[str, Any]] = None
) -> VideoMetadata:
    """
    Enrich metadata with AI-generated improvements.

    This is a placeholder for future enhancement where AI could:
    - Generate better captions
    - Suggest optimal hashtags
    - Recommend posting times
    - Add emojis or formatting

    Args:
        metadata: Original VideoMetadata
        context: Additional context for AI

    Returns:
        Enriched VideoMetadata
    """
    # For now, return the metadata unchanged
    # This is a placeholder for future AI integration
    return metadata


def merge_metadata_sources(
    primary: Dict[str, Any],
    secondary: Dict[str, Any],
    conflict_strategy: str = "primary_first"
) -> Dict[str, Any]:
    """
    Merge metadata from multiple sources.

    Args:
        primary: Primary metadata source
        secondary: Secondary metadata source
        conflict_strategy: How to handle conflicts:
            - "primary_first": Use primary value
            - "secondary_first": Use secondary value
            - "merge_lists": Merge list values
            - "most_recent": Use most recent (by timestamp if available)

    Returns:
        Merged metadata dictionary
    """
    merged = primary.copy()

    for key, value in secondary.items():
        if key not in merged:
            # Key doesn't exist in primary, add it
            merged[key] = value
        elif conflict_strategy == "primary_first":
            # Keep primary value
            continue
        elif conflict_strategy == "secondary_first":
            # Use secondary value
            merged[key] = value
        elif conflict_strategy == "merge_lists":
            # Merge if both are lists
            if isinstance(merged[key], list) and isinstance(value, list):
                merged[key] = merged[key] + value
            else:
                # Fallback to secondary
                merged[key] = value
        elif conflict_strategy == "most_recent":
            # Try to determine most recent based on timestamps
            # This is simplified - would need actual timestamp fields
            merged[key] = value  # Default to secondary

    return merged
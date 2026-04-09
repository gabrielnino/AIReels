"""
Data models for integration between generation and upload systems.

Defines common interfaces and data structures that are independent
of the specific upload implementation (Graph API vs Playwright UI).

Created by: Sam Lead Developer
Date: 2026-04-08
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class UploadStatus(Enum):
    """Status of an upload operation."""
    PENDING = "pending"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class VideoMetadata:
    """
    Metadata for a video to be uploaded to Instagram.

    This structure captures all information needed for upload,
    extracted from the qwen-poc generation pipeline output.
    """
    # Required fields
    video_path: str
    caption: str = ""

    # Optional fields
    hashtags: List[str] = field(default_factory=list)
    location: Optional[str] = None
    schedule_time: Optional[datetime] = None

    # Extended metadata (from qwen-poc, may be used for analytics or enhancements)
    topic: Optional[str] = None
    emotion: Optional[str] = None
    cta: Optional[str] = None  # Call to action
    on_screen_text: Optional[str] = None

    # Technical metadata
    duration_seconds: Optional[float] = None
    file_size_mb: Optional[float] = None
    video_format: Optional[str] = None

    # Privacy and visibility
    is_public: bool = True
    allow_comments: bool = True
    allow_embedding: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        result = {
            "video_path": self.video_path,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "location": self.location,
            "topic": self.topic,
            "emotion": self.emotion,
            "cta": self.cta,
            "on_screen_text": self.on_screen_text,
            "duration_seconds": self.duration_seconds,
            "file_size_mb": self.file_size_mb,
            "video_format": self.video_format,
            "is_public": self.is_public,
            "allow_comments": self.allow_comments,
            "allow_embedding": self.allow_embedding,
        }

        if self.schedule_time:
            result["schedule_time"] = self.schedule_time.isoformat()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoMetadata":
        """Create VideoMetadata from dictionary."""
        # Handle schedule_time conversion
        schedule_time = None
        if "schedule_time" in data and data["schedule_time"]:
            schedule_time = datetime.fromisoformat(data["schedule_time"])

        return cls(
            video_path=data.get("video_path", ""),
            caption=data.get("caption", ""),
            hashtags=data.get("hashtags", []),
            location=data.get("location"),
            schedule_time=schedule_time,
            topic=data.get("topic"),
            emotion=data.get("emotion"),
            cta=data.get("cta"),
            on_screen_text=data.get("on_screen_text"),
            duration_seconds=data.get("duration_seconds"),
            file_size_mb=data.get("file_size_mb"),
            video_format=data.get("video_format"),
            is_public=data.get("is_public", True),
            allow_comments=data.get("allow_comments", True),
            allow_embedding=data.get("allow_embedding", True),
        )


@dataclass
class UploadResult:
    """
    Result of an upload operation.

    Contains information about the success/failure of the upload
    and any relevant identifiers or error messages.
    """
    status: UploadStatus
    upload_id: Optional[str] = None
    media_id: Optional[str] = None  # Instagram media ID if published
    publish_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

    # Performance metrics
    upload_duration_seconds: Optional[float] = None
    processing_duration_seconds: Optional[float] = None
    total_duration_seconds: Optional[float] = None

    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        result = {
            "status": self.status.value,
            "upload_id": self.upload_id,
            "media_id": self.media_id,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "upload_duration_seconds": self.upload_duration_seconds,
            "processing_duration_seconds": self.processing_duration_seconds,
            "total_duration_seconds": self.total_duration_seconds,
            "metadata": self.metadata,
        }

        if self.publish_time:
            result["publish_time"] = self.publish_time.isoformat()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UploadResult":
        """Create UploadResult from dictionary."""
        # Handle publish_time conversion
        publish_time = None
        if "publish_time" in data and data["publish_time"]:
            publish_time = datetime.fromisoformat(data["publish_time"])

        # Handle status enum conversion
        status = UploadStatus(data.get("status", "failed"))

        return cls(
            status=status,
            upload_id=data.get("upload_id"),
            media_id=data.get("media_id"),
            publish_time=publish_time,
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            upload_duration_seconds=data.get("upload_duration_seconds"),
            processing_duration_seconds=data.get("processing_duration_seconds"),
            total_duration_seconds=data.get("total_duration_seconds"),
            metadata=data.get("metadata", {}),
        )

    @property
    def successful(self) -> bool:
        """Check if upload was successful."""
        return self.status == UploadStatus.COMPLETED

    @property
    def failed(self) -> bool:
        """Check if upload failed."""
        return self.status == UploadStatus.FAILED

    @property
    def in_progress(self) -> bool:
        """Check if upload is still in progress."""
        return self.status in [
            UploadStatus.PENDING,
            UploadStatus.PROCESSING,
            UploadStatus.UPLOADING,
            UploadStatus.PUBLISHING,
        ]


@dataclass
class UploadOptions:
    """
    Options for configuring upload behavior.

    These options can be used to control retry logic,
    validation, and other upload parameters.
    """
    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: int = 30

    # Validation
    validate_video: bool = True
    validate_metadata: bool = True

    # Instagram-specific
    use_compression: bool = True
    generate_thumbnails: bool = True

    # Performance
    timeout_seconds: int = 300  # 5 minutes
    chunk_size_mb: int = 10

    # Debugging
    enable_debug_logging: bool = False
    save_debug_files: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert options to dictionary."""
        return {
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "validate_video": self.validate_video,
            "validate_metadata": self.validate_metadata,
            "use_compression": self.use_compression,
            "generate_thumbnails": self.generate_thumbnails,
            "timeout_seconds": self.timeout_seconds,
            "chunk_size_mb": self.chunk_size_mb,
            "enable_debug_logging": self.enable_debug_logging,
            "save_debug_files": self.save_debug_files,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UploadOptions":
        """Create UploadOptions from dictionary."""
        return cls(
            max_retries=data.get("max_retries", 3),
            retry_delay_seconds=data.get("retry_delay_seconds", 30),
            validate_video=data.get("validate_video", True),
            validate_metadata=data.get("validate_metadata", True),
            use_compression=data.get("use_compression", True),
            generate_thumbnails=data.get("generate_thumbnails", True),
            timeout_seconds=data.get("timeout_seconds", 300),
            chunk_size_mb=data.get("chunk_size_mb", 10),
            enable_debug_logging=data.get("enable_debug_logging", False),
            save_debug_files=data.get("save_debug_files", False),
        )
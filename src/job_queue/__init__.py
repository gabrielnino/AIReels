"""
Job Queue System for AIReels.

This package provides a job queue system for batch processing of
Instagram upload jobs with priorities, retry logic, and persistence.

Modules:
    job_manager: Main job manager and queue implementation
"""

from .job_manager import (
    JobManager,
    Job,
    JobStatus,
    JobPriority,
    create_instagram_upload_handler,
)

__all__ = [
    'JobManager',
    'Job',
    'JobStatus',
    'JobPriority',
    'create_instagram_upload_handler',
]

__version__ = '0.1.0'
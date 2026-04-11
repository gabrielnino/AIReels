"""
Job Manager for batch processing queue system.

This module provides a simple queue system for batch processing of
Instagram upload jobs with priorities, retry logic, and persistence.

Created by: Sam Lead Developer
Date: 2026-04-11
"""

import asyncio
import json
import time
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import pickle
import sqlite3
from concurrent.futures import ThreadPoolExecutor


class JobStatus(Enum):
    """Status of a job in the queue."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Priority levels for jobs."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Job:
    """Represents a job in the queue."""
    # Core fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_type: str = "instagram_upload"
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Job data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Execution info
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    # Timing
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        result = asdict(self)

        # Convert enums to strings
        result['status'] = self.status.value
        result['priority'] = self.priority.value

        # Convert datetimes to ISO format
        for field in ['created_at', 'updated_at', 'started_at', 'completed_at', 'scheduled_for']:
            if result[field]:
                result[field] = result[field].isoformat()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create job from dictionary."""
        # Convert string enums back to enum values
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = JobStatus(data['status'])
        if 'priority' in data and isinstance(data['priority'], (str, int)):
            if isinstance(data['priority'], str):
                data['priority'] = JobPriority[data['priority'].upper()]
            else:
                # Convert numeric priority to enum
                priority_map = {p.value: p for p in JobPriority}
                data['priority'] = priority_map.get(data['priority'], JobPriority.NORMAL)

        # Convert ISO strings back to datetimes
        datetime_fields = ['created_at', 'updated_at', 'started_at', 'completed_at', 'scheduled_for']
        for field in datetime_fields:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)

    def update_status(self, status: JobStatus, error: Optional[str] = None):
        """Update job status and timestamp."""
        self.status = status
        self.updated_at = datetime.now()

        if error:
            self.last_error = error

        if status == JobStatus.PROCESSING and not self.started_at:
            self.started_at = datetime.now()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            self.completed_at = datetime.now()
            if self.started_at:
                self.processing_time = (self.completed_at - self.started_at).total_seconds()

    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return (
            self.status == JobStatus.FAILED and
            self.attempts < self.max_attempts
        )

    def prepare_for_retry(self) -> bool:
        """Prepare job for retry."""
        if not self.can_retry():
            return False

        self.attempts += 1
        self.status = JobStatus.RETRYING
        self.updated_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.processing_time = None

        # Add delay for retry (exponential backoff)
        delay_minutes = min(60, 5 * (2 ** (self.attempts - 1)))  # 5, 10, 20, 40, 60 min
        self.scheduled_for = datetime.now() + timedelta(minutes=delay_minutes)

        return True


class JobQueue:
    """In-memory job queue with priority support."""

    def __init__(self):
        """Initialize empty job queue."""
        self._queues = {
            JobPriority.URGENT: [],
            JobPriority.HIGH: [],
            JobPriority.NORMAL: [],
            JobPriority.LOW: [],
        }
        self._jobs = {}  # job_id -> Job
        self._lock = asyncio.Lock()

    async def add_job(self, job: Job) -> str:
        """Add a job to the queue."""
        async with self._lock:
            self._jobs[job.id] = job
            self._queues[job.priority].append(job.id)
            return job.id

    async def get_next_job(self) -> Optional[Job]:
        """Get the next job to process (by priority)."""
        async with self._lock:
            for priority in [JobPriority.URGENT, JobPriority.HIGH, JobPriority.NORMAL, JobPriority.LOW]:
                if self._queues[priority]:
                    job_id = self._queues[priority].pop(0)
                    job = self._jobs.get(job_id)
                    if job and job.status == JobStatus.PENDING:
                        job.update_status(JobStatus.PROCESSING)
                        return job
            return None

    async def update_job(self, job: Job):
        """Update a job in the queue."""
        async with self._lock:
            self._jobs[job.id] = job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        async with self._lock:
            return self._jobs.get(job_id)

    async def remove_job(self, job_id: str) -> bool:
        """Remove a job from the queue."""
        async with self._lock:
            if job_id in self._jobs:
                # Remove from priority queues
                for queue in self._queues.values():
                    if job_id in queue:
                        queue.remove(job_id)
                # Remove from jobs dict
                del self._jobs[job_id]
                return True
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        async with self._lock:
            stats = {
                'total_jobs': len(self._jobs),
                'by_priority': {},
                'by_status': {},
            }

            # Count by priority
            for priority, queue in self._queues.items():
                stats['by_priority'][priority.value] = len(queue)

            # Count by status
            for job in self._jobs.values():
                status = job.status.value
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            return stats


class JobManager:
    """
    Manages job processing with workers, persistence, and monitoring.

    Features:
    - Priority-based job queue
    - Configurable worker pool
    - Automatic retry with exponential backoff
    - SQLite persistence
    - Job progress tracking
    - Error handling and logging
    """

    def __init__(
        self,
        storage_path: Optional[Union[str, Path]] = None,
        max_workers: int = 3,
        poll_interval: float = 1.0,
        auto_start: bool = True
    ):
        """
        Initialize job manager.

        Args:
            storage_path: Path for SQLite database (None for in-memory only)
            max_workers: Maximum number of concurrent workers
            poll_interval: How often to check for new jobs (seconds)
            auto_start: Whether to start processing automatically
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.max_workers = max_workers
        self.poll_interval = poll_interval
        self.auto_start = auto_start

        self.queue = JobQueue()
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Worker pool executor for CPU-bound tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)

        # Job handlers by type
        self.handlers: Dict[str, Callable] = {}

        # Initialize storage if path provided
        self.db_conn = None
        if self.storage_path:
            self._init_storage()

    def _init_storage(self):
        """Initialize SQLite database for persistence."""
        if not self.storage_path:
            return

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_conn = sqlite3.connect(str(self.storage_path))
        cursor = self.db_conn.cursor()

        # Create jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                data TEXT NOT NULL,
                metadata TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                max_attempts INTEGER NOT NULL,
                last_error TEXT,
                result TEXT,
                scheduled_for TEXT,
                started_at TEXT,
                completed_at TEXT,
                processing_time REAL
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON jobs (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON jobs (priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled ON jobs (scheduled_for)')

        self.db_conn.commit()
        self.logger.info(f"Storage initialized at: {self.storage_path}")

    def register_handler(self, job_type: str, handler: Callable):
        """Register a handler for a specific job type."""
        self.handlers[job_type] = handler
        self.logger.info(f"Registered handler for job type: {job_type}")

    async def start(self):
        """Start the job manager and workers."""
        if self.is_running:
            self.logger.warning("Job manager is already running")
            return

        self.is_running = True
        self.logger.info(f"Starting job manager with {self.max_workers} workers")

        # Load jobs from storage
        await self._load_persisted_jobs()

        # Start worker tasks
        for i in range(self.max_workers):
            worker_task = asyncio.create_task(
                self._worker_loop(f"worker-{i+1}"),
                name=f"job-worker-{i+1}"
            )
            self.workers.append(worker_task)

        # Start maintenance task
        self.maintenance_task = asyncio.create_task(
            self._maintenance_loop(),
            name="job-maintenance"
        )

        self.logger.info("Job manager started successfully")

    async def stop(self, timeout: float = 30.0):
        """Stop the job manager and wait for workers to finish."""
        if not self.is_running:
            return

        self.logger.info("Stopping job manager...")
        self.is_running = False

        # Cancel maintenance task
        if hasattr(self, 'maintenance_task'):
            self.maintenance_task.cancel()

        # Wait for workers to finish current jobs
        if self.workers:
            self.logger.info(f"Waiting for {len(self.workers)} workers to finish...")
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.workers, return_exceptions=True),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                self.logger.warning("Timeout waiting for workers to finish")
                # Cancel remaining workers
                for worker in self.workers:
                    if not worker.done():
                        worker.cancel()

        # Close storage
        if self.db_conn:
            self.db_conn.close()

        self.logger.info("Job manager stopped")

    async def submit_job(
        self,
        job_type: str,
        data: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        max_attempts: int = 3,
        scheduled_for: Optional[datetime] = None
    ) -> str:
        """Submit a new job to the queue."""
        job = Job(
            job_type=job_type,
            priority=priority,
            data=data,
            metadata=metadata or {},
            max_attempts=max_attempts,
            scheduled_for=scheduled_for
        )

        # Add to in-memory queue
        job_id = await self.queue.add_job(job)

        # Persist to storage
        if self.db_conn:
            await self._persist_job(job)

        self.logger.info(f"Submitted job {job_id} (type: {job_type}, priority: {priority.value})")
        return job_id

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a job."""
        job = await self.queue.get_job(job_id)
        if job:
            return job.to_dict()
        return None

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job = await self.queue.get_job(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.RETRYING]:
            job.update_status(JobStatus.CANCELLED)
            await self.queue.update_job(job)

            if self.db_conn:
                await self._persist_job(job)

            self.logger.info(f"Cancelled job {job_id}")
            return True

        self.logger.warning(f"Cannot cancel job {job_id}: status={job.status if job else 'not found'}")
        return False

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the queue."""
        stats = await self.queue.get_stats()

        if self.db_conn:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM jobs')
            total_persisted = cursor.fetchone()[0]
            stats['total_persisted'] = total_persisted

        return stats

    async def _worker_loop(self, worker_name: str):
        """Worker loop that processes jobs from the queue."""
        self.logger.info(f"Worker {worker_name} started")

        while self.is_running:
            try:
                # Get next job
                job = await self.queue.get_next_job()

                if not job:
                    # No jobs available, wait and try again
                    await asyncio.sleep(self.poll_interval)
                    continue

                # Check if job is scheduled for future
                if job.scheduled_for and job.scheduled_for > datetime.now():
                    # Put back in queue and wait
                    job.update_status(JobStatus.PENDING)
                    await self.queue.add_job(job)
                    await asyncio.sleep(self.poll_interval)
                    continue

                # Process the job
                self.logger.info(f"Worker {worker_name} processing job {job.id}")
                await self._process_job(job, worker_name)

            except asyncio.CancelledError:
                self.logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

        self.logger.info(f"Worker {worker_name} stopped")

    async def _process_job(self, job: Job, worker_name: str):
        """Process a single job."""
        try:
            # Get handler for job type
            handler = self.handlers.get(job.job_type)
            if not handler:
                error_msg = f"No handler registered for job type: {job.job_type}"
                job.update_status(JobStatus.FAILED, error_msg)
                await self.queue.update_job(job)

                if self.db_conn:
                    await self._persist_job(job)

                self.logger.error(f"Job {job.id} failed: {error_msg}")
                return

            # Execute handler
            result = await handler(job.data)

            # Update job with result
            job.result = result
            job.update_status(JobStatus.COMPLETED)

            self.logger.info(f"Worker {worker_name} completed job {job.id}")

        except Exception as e:
            # Job failed
            error_msg = str(e)
            job.update_status(JobStatus.FAILED, error_msg)

            # Check if job can be retried
            if job.can_retry():
                job.prepare_for_retry()
                await self.queue.add_job(job)
                self.logger.warning(f"Job {job.id} failed, scheduled for retry (attempt {job.attempts}/{job.max_attempts})")
            else:
                self.logger.error(f"Job {job.id} failed permanently: {error_msg}")

        # Update job in queue and storage
        await self.queue.update_job(job)
        if self.db_conn:
            await self._persist_job(job)

    async def _maintenance_loop(self):
        """Maintenance loop for cleanup and monitoring."""
        self.logger.info("Maintenance loop started")

        while self.is_running:
            try:
                await asyncio.sleep(60)  # Run every minute

                # Clean up old completed jobs
                await self._cleanup_old_jobs()

                # Log stats
                stats = await self.get_queue_stats()
                self.logger.debug(f"Queue stats: {stats}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Maintenance error: {e}", exc_info=True)

        self.logger.info("Maintenance loop stopped")

    async def _persist_job(self, job: Job):
        """Persist job to SQLite database."""
        if not self.db_conn:
            return

        try:
            cursor = self.db_conn.cursor()

            # Convert job to dict and serialize JSON fields
            job_dict = job.to_dict()
            data_json = json.dumps(job_dict['data'])
            metadata_json = json.dumps(job_dict['metadata'])
            result_json = json.dumps(job_dict['result']) if job_dict['result'] else None

            # Insert or replace
            cursor.execute('''
                INSERT OR REPLACE INTO jobs
                (id, job_type, status, priority, created_at, updated_at, data, metadata,
                 attempts, max_attempts, last_error, result, scheduled_for, started_at,
                 completed_at, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_dict['id'],
                job_dict['job_type'],
                job_dict['status'],
                job_dict['priority'],
                job_dict['created_at'],
                job_dict['updated_at'],
                data_json,
                metadata_json,
                job_dict['attempts'],
                job_dict['max_attempts'],
                job_dict['last_error'],
                result_json,
                job_dict.get('scheduled_for'),
                job_dict.get('started_at'),
                job_dict.get('completed_at'),
                job_dict.get('processing_time')
            ))

            self.db_conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to persist job {job.id}: {e}", exc_info=True)

    async def _load_persisted_jobs(self):
        """Load persisted jobs from SQLite database."""
        if not self.db_conn:
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT * FROM jobs WHERE status IN (?, ?, ?)',
                          (JobStatus.PENDING.value, JobStatus.RETRYING.value, JobStatus.PROCESSING.value))

            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            for row in rows:
                try:
                    # Convert row to dict
                    row_dict = dict(zip(column_names, row))

                    # Parse JSON fields
                    if row_dict['data']:
                        row_dict['data'] = json.loads(row_dict['data'])
                    if row_dict['metadata']:
                        row_dict['metadata'] = json.loads(row_dict['metadata'])
                    if row_dict['result']:
                        row_dict['result'] = json.loads(row_dict['result'])

                    # Create job and add to queue
                    job = Job.from_dict(row_dict)

                    # Only add if not already in memory (e.g., after restart)
                    existing_job = await self.queue.get_job(job.id)
                    if not existing_job:
                        await self.queue.add_job(job)
                        self.logger.info(f"Loaded persisted job {job.id} (status: {job.status.value})")

                except Exception as e:
                    self.logger.error(f"Failed to load persisted job: {e}", exc_info=True)

            self.logger.info(f"Loaded {len(rows)} persisted jobs from storage")

        except Exception as e:
            self.logger.error(f"Failed to load persisted jobs: {e}", exc_info=True)

    async def _cleanup_old_jobs(self, days_to_keep: int = 7):
        """Clean up old completed/failed/cancelled jobs from storage."""
        if not self.db_conn:
            return

        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_iso = cutoff_date.isoformat()

            cursor = self.db_conn.cursor()
            cursor.execute(
                'DELETE FROM jobs WHERE completed_at < ? AND status IN (?, ?, ?)',
                (cutoff_iso, JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value)
            )

            deleted_count = cursor.rowcount
            self.db_conn.commit()

            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old jobs (older than {days_to_keep} days)")

        except Exception as e:
            self.logger.error(f"Failed to cleanup old jobs: {e}", exc_info=True)


# Example usage and factory functions

async def create_instagram_upload_handler(pipeline_bridge):
    """Create a handler for Instagram upload jobs."""
    async def handler(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Instagram upload job."""
        # Extract data from job
        qwen_output = job_data.get('qwen_output', {})
        options_dict = job_data.get('options', {})
        enrich_with_ai = job_data.get('enrich_with_ai', False)

        # Convert options dict to UploadOptions if needed
        from integration.data_models import UploadOptions
        options = UploadOptions.from_dict(options_dict) if options_dict else UploadOptions()

        # Process and upload
        result = await pipeline_bridge.process_and_upload_with_retry(
            qwen_output, options, enrich_with_ai
        )

        return {
            'success': result.successful,
            'status': result.status.value,
            'media_id': result.media_id,
            'error_message': result.error_message,
            'duration_seconds': result.total_duration_seconds,
            'retry_count': result.retry_count,
        }

    return handler


async def example_usage():
    """Example usage of JobManager."""
    print("JobManager Example Usage")
    print("=" * 60)

    # Create job manager with persistence
    job_manager = JobManager(
        storage_path="./data/jobs.db",
        max_workers=2,
        poll_interval=0.5
    )

    # Register a simple handler
    async def test_handler(data):
        print(f"Processing test job with data: {data}")
        await asyncio.sleep(1)  # Simulate work
        return {"processed": True, "input": data}

    job_manager.register_handler("test_job", test_handler)

    # Start job manager
    await job_manager.start()

    # Submit some test jobs
    job_ids = []
    for i in range(5):
        job_id = await job_manager.submit_job(
            job_type="test_job",
            data={"task_id": i, "message": f"Test job {i}"},
            priority=JobPriority.NORMAL if i % 2 == 0 else JobPriority.HIGH
        )
        job_ids.append(job_id)
        print(f"Submitted job {job_id}")

    # Wait for jobs to complete
    print("\nWaiting for jobs to complete...")
    await asyncio.sleep(10)

    # Get status of jobs
    print("\nJob statuses:")
    for job_id in job_ids:
        status = await job_manager.get_job_status(job_id)
        if status:
            print(f"  {job_id}: {status['status']} (attempts: {status['attempts']})")

    # Get queue stats
    stats = await job_manager.get_queue_stats()
    print(f"\nQueue stats: {stats}")

    # Stop job manager
    await job_manager.stop()
    print("\nExample completed!")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
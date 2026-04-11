"""
Monitoring Dashboard for AIReels.

A simple web dashboard to monitor:
- Job queue status
- Upload statistics
- System health
- Recent activities

Created by: Sam Lead Developer
Date: 2026-04-11
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from flask import Flask, render_template, jsonify, request, Response
import sqlite3


class DashboardStatus(Enum):
    """Dashboard status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class SystemMetrics:
    """System metrics for monitoring."""
    # Queue metrics
    total_jobs: int = 0
    pending_jobs: int = 0
    processing_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0

    # Performance metrics
    avg_processing_time: float = 0.0
    success_rate: float = 0.0
    throughput_last_hour: int = 0

    # System health
    uptime_hours: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0

    # Timestamps
    last_update: datetime = field(default_factory=datetime.now)
    startup_time: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['last_update'] = self.last_update.isoformat()
        result['startup_time'] = self.startup_time.isoformat()
        return result


@dataclass
class JobSummary:
    """Summary of a job for the dashboard."""
    id: str
    job_type: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    attempts: int = 0
    processing_time: Optional[float] = None
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        if self.processing_time is None:
            result.pop('processing_time')
        return result


class MonitoringDashboard:
    """
    Web dashboard for monitoring AIReels system.

    Features:
    - Real-time job queue monitoring
    - System health metrics
    - Upload statistics
    - Historical data visualization
    - API endpoints for external integration
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        db_path: Optional[str] = None,
        update_interval: int = 5
    ):
        """
        Initialize monitoring dashboard.

        Args:
            host: Host to bind the server to
            port: Port to listen on
            db_path: Path to SQLite database (None for default)
            update_interval: How often to update metrics (seconds)
        """
        self.host = host
        self.port = port
        self.db_path = Path(db_path) if db_path else Path("./data/jobs.db")
        self.update_interval = update_interval

        # Create Flask app
        self.app = Flask(__name__)
        self._setup_routes()

        # Metrics
        self.metrics = SystemMetrics()
        self.recent_jobs: List[JobSummary] = []
        self.job_manager = None  # Will be set by set_job_manager()

        # Dashboard status
        self.status = DashboardStatus.OFFLINE
        self.last_metrics_update = datetime.now()

    def set_job_manager(self, job_manager):
        """Set the job manager instance for real-time monitoring."""
        self.job_manager = job_manager

    def _setup_routes(self):
        """Setup Flask routes."""
        # Main pages
        self.app.route('/')(self.index)
        self.app.route('/dashboard')(self.dashboard)
        self.app.route('/jobs')(self.jobs_page)
        self.app.route('/metrics')(self.metrics_page)
        self.app.route('/api')(self.api_docs)

        # API endpoints
        self.app.route('/api/health')(self.api_health)
        self.app.route('/api/metrics')(self.api_metrics)
        self.app.route('/api/jobs')(self.api_jobs)
        self.app.route('/api/jobs/<job_id>')(self.api_job_detail)
        self.app.route('/api/stats')(self.api_stats)
        self.app.route('/api/history')(self.api_history)

        # Static file serving
        self.app.route('/static/<path:filename>')(self.serve_static)

    def index(self):
        """Home page."""
        return render_template('index.html',
                             status=self.status.value,
                             metrics=self.metrics.to_dict(),
                             recent_jobs=[j.to_dict() for j in self.recent_jobs[:10]])

    def dashboard(self):
        """Main dashboard page."""
        return render_template('dashboard.html',
                             status=self.status.value,
                             metrics=self.metrics.to_dict())

    def jobs_page(self):
        """Jobs monitoring page."""
        return render_template('jobs.html',
                             jobs=[j.to_dict() for j in self.recent_jobs],
                             total_jobs=len(self.recent_jobs))

    def metrics_page(self):
        """System metrics page."""
        return render_template('metrics.html',
                             metrics=self.metrics.to_dict())

    def api_docs(self):
        """API documentation page."""
        return render_template('api_docs.html')

    def api_health(self):
        """Health check endpoint."""
        health_status = {
            "status": self.status.value,
            "timestamp": datetime.now().isoformat(),
            "uptime_hours": self.metrics.uptime_hours,
            "database": "connected" if self._check_database() else "disconnected",
            "job_manager": "connected" if self.job_manager else "disconnected",
        }
        return jsonify(health_status)

    def api_metrics(self):
        """Get current metrics."""
        return jsonify(self.metrics.to_dict())

    def api_jobs(self):
        """Get recent jobs."""
        limit = request.args.get('limit', 100, type=int)
        status = request.args.get('status', None)
        job_type = request.args.get('type', None)

        jobs = self.recent_jobs[:limit]

        # Filter by status if provided
        if status:
            jobs = [j for j in jobs if j.status == status]

        # Filter by job type if provided
        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]

        return jsonify({
            "jobs": [j.to_dict() for j in jobs],
            "count": len(jobs),
            "filters": {
                "status": status,
                "type": job_type,
                "limit": limit
            }
        })

    def api_job_detail(self, job_id: str):
        """Get detailed information about a specific job."""
        # Try to get from recent jobs first
        for job in self.recent_jobs:
            if job.id == job_id:
                return jsonify(job.to_dict())

        # Try to get from database
        job_detail = self._get_job_from_db(job_id)
        if job_detail:
            return jsonify(job_detail)

        return jsonify({"error": "Job not found"}), 404

    def api_stats(self):
        """Get statistics."""
        stats = {
            "queue_stats": self._get_queue_stats(),
            "performance_stats": self._get_performance_stats(),
            "system_stats": self._get_system_stats(),
            "timestamp": datetime.now().isoformat(),
        }
        return jsonify(stats)

    def api_history(self):
        """Get historical data."""
        hours = request.args.get('hours', 24, type=int)
        metric = request.args.get('metric', 'jobs_completed')

        history = self._get_historical_data(hours, metric)
        return jsonify({
            "metric": metric,
            "hours": hours,
            "data": history,
            "timestamp": datetime.now().isoformat(),
        })

    def serve_static(self, filename: str):
        """Serve static files."""
        static_dir = Path(__file__).parent / "static"
        file_path = static_dir / filename

        if not file_path.exists() or not file_path.is_file():
            return "File not found", 404

        return self.app.send_static_file(str(file_path.relative_to(static_dir)))

    async def update_metrics(self):
        """Update dashboard metrics."""
        while True:
            try:
                # Update metrics from job manager if available
                if self.job_manager:
                    stats = await self.job_manager.get_queue_stats()
                    self.metrics.total_jobs = stats.get('total_jobs', 0)
                    self.metrics.pending_jobs = stats.get('by_status', {}).get('pending', 0)
                    self.metrics.processing_jobs = stats.get('by_status', {}).get('processing', 0)
                    self.metrics.completed_jobs = stats.get('by_status', {}).get('completed', 0)
                    self.metrics.failed_jobs = stats.get('by_status', {}).get('failed', 0)

                    # Calculate success rate
                    total_processed = self.metrics.completed_jobs + self.metrics.failed_jobs
                    if total_processed > 0:
                        self.metrics.success_rate = (
                            self.metrics.completed_jobs / total_processed * 100
                        )

                # Update recent jobs from database
                self.recent_jobs = await self._get_recent_jobs(limit=50)

                # Update system health
                self._update_system_health()

                # Update dashboard status
                self._update_dashboard_status()

                # Update timestamp
                self.metrics.last_update = datetime.now()
                self.last_metrics_update = datetime.now()

                # Calculate uptime
                self.metrics.uptime_hours = (
                    datetime.now() - self.metrics.startup_time
                ).total_seconds() / 3600

                self.status = DashboardStatus.HEALTHY

            except Exception as e:
                print(f"Error updating metrics: {e}")
                self.status = DashboardStatus.ERROR

            await asyncio.sleep(self.update_interval)

    def _update_system_health(self):
        """Update system health metrics (simulated for now)."""
        # Simulated metrics - in production would use psutil or similar
        import random
        self.metrics.memory_usage_mb = random.uniform(100, 500)
        self.metrics.cpu_usage_percent = random.uniform(5, 30)
        self.metrics.disk_usage_percent = random.uniform(20, 60)

        # Calculate average processing time from recent completed jobs
        completed_jobs = [j for j in self.recent_jobs if j.status == 'completed' and j.processing_time]
        if completed_jobs:
            self.metrics.avg_processing_time = sum(
                j.processing_time for j in completed_jobs
            ) / len(completed_jobs)

        # Calculate throughput (jobs per hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_completed = [
            j for j in self.recent_jobs
            if j.status == 'completed' and j.updated_at > one_hour_ago
        ]
        self.metrics.throughput_last_hour = len(recent_completed)

    def _update_dashboard_status(self):
        """Update dashboard status based on metrics."""
        if self.metrics.failed_jobs > self.metrics.completed_jobs:
            self.status = DashboardStatus.ERROR
        elif self.metrics.failed_jobs > 0:
            self.status = DashboardStatus.WARNING
        else:
            self.status = DashboardStatus.HEALTHY

    def _check_database(self) -> bool:
        """Check if database is accessible."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.close()
            return True
        except:
            return False

    async def _get_recent_jobs(self, limit: int = 50) -> List[JobSummary]:
        """Get recent jobs from database."""
        jobs = []

        if not self.db_path.exists():
            return jobs

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, job_type, status, priority, created_at, updated_at,
                       attempts, processing_time, last_error
                FROM jobs
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

            for row in cursor.fetchall():
                job = JobSummary(
                    id=row[0],
                    job_type=row[1],
                    status=row[2],
                    priority=row[3],
                    created_at=datetime.fromisoformat(row[4]),
                    updated_at=datetime.fromisoformat(row[5]),
                    attempts=row[6],
                    processing_time=row[7],
                    last_error=row[8]
                )
                jobs.append(job)

            conn.close()
        except Exception as e:
            print(f"Error getting recent jobs: {e}")

        return jobs

    def _get_job_from_db(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details from database."""
        if not self.db_path.exists():
            return None

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM jobs WHERE id = ?
            ''', (job_id,))

            row = cursor.fetchone()
            if not row:
                return None

            column_names = [desc[0] for desc in cursor.description]
            job_dict = dict(zip(column_names, row))

            # Parse JSON fields
            for field in ['data', 'metadata', 'result']:
                if job_dict.get(field):
                    job_dict[field] = json.loads(job_dict[field])

            conn.close()
            return job_dict

        except Exception as e:
            print(f"Error getting job from DB: {e}")
            return None

    def _get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "total": self.metrics.total_jobs,
            "pending": self.metrics.pending_jobs,
            "processing": self.metrics.processing_jobs,
            "completed": self.metrics.completed_jobs,
            "failed": self.metrics.failed_jobs,
            "success_rate": round(self.metrics.success_rate, 1),
        }

    def _get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "avg_processing_time": round(self.metrics.avg_processing_time, 2),
            "throughput_last_hour": self.metrics.throughput_last_hour,
            "uptime_hours": round(self.metrics.uptime_hours, 2),
        }

    def _get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "memory_usage_mb": round(self.metrics.memory_usage_mb, 1),
            "cpu_usage_percent": round(self.metrics.cpu_usage_percent, 1),
            "disk_usage_percent": round(self.metrics.disk_usage_percent, 1),
        }

    def _get_historical_data(self, hours: int, metric: str) -> List[Dict[str, Any]]:
        """Get historical data for charts (simulated for now)."""
        # Simulated data - in production would query database
        data = []
        now = datetime.now()

        for i in range(hours):
            timestamp = now - timedelta(hours=i)
            value = 0

            if metric == 'jobs_completed':
                value = self.metrics.completed_jobs // hours + (i % 3)
            elif metric == 'success_rate':
                value = 80 + (i % 20)
            elif metric == 'processing_time':
                value = 5 + (i % 10)
            elif metric == 'queue_size':
                value = self.metrics.pending_jobs + (i % 5)

            data.append({
                "timestamp": timestamp.isoformat(),
                "value": value
            })

        return list(reversed(data))

    def run(self):
        """Run the dashboard server."""
        print(f"🚀 Starting AIReels Monitoring Dashboard on http://{self.host}:{self.port}")
        print(f"📊 Database: {self.db_path}")
        print(f"📈 Update interval: {self.update_interval}s")

        # Start metrics update in background
        import threading
        metrics_thread = threading.Thread(
            target=lambda: asyncio.run(self.update_metrics()),
            daemon=True
        )
        metrics_thread.start()

        # Run Flask app
        self.app.run(host=self.host, port=self.port, debug=False)


# Command-line interface
def main():
    """Run the dashboard from command line."""
    import argparse

    parser = argparse.ArgumentParser(description='AIReels Monitoring Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--db', default='./data/jobs.db', help='Path to jobs database')
    parser.add_argument('--interval', type=int, default=5, help='Metrics update interval (seconds)')

    args = parser.parse_args()

    # Create and run dashboard
    dashboard = MonitoringDashboard(
        host=args.host,
        port=args.port,
        db_path=args.db,
        update_interval=args.interval
    )

    dashboard.run()


if __name__ == "__main__":
    main()
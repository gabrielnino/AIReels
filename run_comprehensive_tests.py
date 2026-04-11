#!/usr/bin/env python3
"""
Comprehensive test suite for AIReels Sprint 3.

Tests all components of the pipeline:
1. Integration module
2. Job queue system
3. Monitoring dashboard
4. End-to-end flow

Created by: Sam Lead Developer
Date: 2026-04-11
"""

import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path
import subprocess
import time

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'=' * 70}")
    print(f"🧪 {title}")
    print(f"{'=' * 70}")

def print_result(test_name, success, message=""):
    """Print test result."""
    emoji = "✅" if success else "❌"
    print(f"{emoji} {test_name}: {message}")

async def test_integration_module():
    """Test the integration module."""
    print_header("TEST 1: Integration Module")

    results = []

    try:
        # Test data models
        from integration.data_models import VideoMetadata, UploadResult, UploadStatus, UploadOptions

        # Test 1.1: VideoMetadata creation
        metadata = VideoMetadata(
            video_path="/tmp/test.mp4",
            caption="Test caption",
            hashtags=["#test", "#demo"],
            topic="Testing",
            emotion="happy"
        )
        assert metadata.video_path == "/tmp/test.mp4"
        assert metadata.caption == "Test caption"
        results.append(("VideoMetadata creation", True))

        # Test 1.2: UploadOptions
        options = UploadOptions(max_retries=5, retry_delay_seconds=10)
        assert options.max_retries == 5
        assert options.retry_delay_seconds == 10
        results.append(("UploadOptions configuration", True))

        # Test 1.3: Metadata adapter
        from integration.metadata_adapter import adapt_qwen_to_upload, validate_metadata

        # Create test video file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b'test video content')
            test_video = f.name

        try:
            qwen_output = {
                "final_video_path": test_video,
                "caption": "Test video #testing",
                "hashtags": ["#testing", "#demo"],
                "topic": "Integration Testing"
            }

            metadata = adapt_qwen_to_upload(qwen_output, UploadOptions(validate_video=False))
            assert metadata.video_path == test_video
            results.append(("Metadata adapter", True))

        finally:
            if os.path.exists(test_video):
                os.unlink(test_video)

        # Test 1.4: Mock uploader
        from integration.mock_uploader import MockInstagramUploader
        from integration.pipeline_bridge import PipelineBridge

        uploader = MockInstagramUploader(success_rate=1.0, average_delay_seconds=0.1)
        bridge = PipelineBridge(uploader)

        # Create another test file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b'test content')
            test_video = f.name

        try:
            qwen_output = {
                "final_video_path": test_video,
                "caption": "Mock upload test",
                "hashtags": ["#mock"],
                "topic": "Mock Test"
            }

            result = await bridge.process_and_upload(qwen_output, UploadOptions(validate_video=False))
            assert result.successful
            results.append(("Mock uploader integration", True))

        finally:
            if os.path.exists(test_video):
                os.unlink(test_video)

    except Exception as e:
        results.append(("Integration module tests", False, f"Error: {type(e).__name__}: {e}"))

    # Print results
    for test_name, success, *msg in results:
        print_result(test_name, success, msg[0] if msg else "")

    return all(success for success, *_ in results)

async def test_job_queue_system():
    """Test the job queue system."""
    print_header("TEST 2: Job Queue System")

    results = []

    try:
        from job_queue.job_manager import JobManager, Job, JobStatus, JobPriority

        # Test 2.1: Job creation
        job = Job(
            job_type="test_job",
            priority=JobPriority.HIGH,
            data={"test": "data"}
        )
        assert job.job_type == "test_job"
        assert job.priority == JobPriority.HIGH
        results.append(("Job creation", True))

        # Test 2.2: Job status updates
        job.update_status(JobStatus.PROCESSING)
        assert job.status == JobStatus.PROCESSING
        assert job.started_at is not None
        results.append(("Job status updates", True))

        # Test 2.3: Job retry logic
        job.attempts = 1
        job.max_attempts = 3
        job.status = JobStatus.FAILED
        assert job.can_retry()
        results.append(("Job retry logic", True))

        # Test 2.4: JobManager with in-memory storage
        job_manager = JobManager(
            storage_path=None,  # In-memory only
            max_workers=1,
            poll_interval=0.1,
            auto_start=False
        )

        # Register test handler
        async def test_handler(data):
            await asyncio.sleep(0.1)
            return {"processed": True, "data": data}

        job_manager.register_handler("test_job", test_handler)

        # Submit a job
        job_id = await job_manager.submit_job(
            job_type="test_job",
            data={"message": "test"},
            priority=JobPriority.NORMAL
        )
        assert job_id is not None
        results.append(("Job submission", True))

        # Start job manager
        await job_manager.start()

        # Wait for job to complete
        await asyncio.sleep(0.5)

        # Get job status
        status = await job_manager.get_job_status(job_id)
        assert status is not None
        assert status['status'] in ['completed', 'processing', 'pending']
        results.append(("Job status retrieval", True))

        # Get queue stats
        stats = await job_manager.get_queue_stats()
        assert 'total_jobs' in stats
        results.append(("Queue statistics", True))

        # Stop job manager
        await job_manager.stop()
        results.append(("Job manager lifecycle", True))

    except Exception as e:
        results.append(("Job queue system tests", False, f"Error: {type(e).__name__}: {e}"))

    # Print results
    for test_name, success, *msg in results:
        print_result(test_name, success, msg[0] if msg else "")

    return all(success for success, *_ in results)

async def test_monitoring_dashboard():
    """Test the monitoring dashboard."""
    print_header("TEST 3: Monitoring Dashboard")

    results = []

    try:
        from monitoring.dashboard import MonitoringDashboard, SystemMetrics, JobSummary

        # Test 3.1: SystemMetrics
        metrics = SystemMetrics(
            total_jobs=100,
            pending_jobs=10,
            completed_jobs=85,
            failed_jobs=5,
            success_rate=94.4
        )
        assert metrics.total_jobs == 100
        assert metrics.success_rate == 94.4
        results.append(("SystemMetrics creation", True))

        # Test 3.2: JobSummary
        job = JobSummary(
            id="test-id",
            job_type="instagram_upload",
            status="completed",
            priority="high",
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            updated_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            attempts=1,
            processing_time=5.5
        )
        assert job.id == "test-id"
        assert job.job_type == "instagram_upload"
        results.append(("JobSummary creation", True))

        # Test 3.3: Dashboard initialization
        dashboard = MonitoringDashboard(
            host="127.0.0.1",
            port=9999,  # Use non-standard port for testing
            update_interval=10
        )
        assert dashboard.host == "127.0.0.1"
        assert dashboard.port == 9999
        results.append(("Dashboard initialization", True))

        # Test 3.4: API routes exist
        with dashboard.app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'status' in data
            results.append(("Health endpoint", True))

        results.append(("Dashboard API", True))

    except Exception as e:
        results.append(("Monitoring dashboard tests", False, f"Error: {type(e).__name__}: {e}"))

    # Print results
    for test_name, success, *msg in results:
        print_result(test_name, success, msg[0] if msg else "")

    return all(success for success, *_ in results)

async def test_end_to_end_flow():
    """Test end-to-end flow with mock components."""
    print_header("TEST 4: End-to-End Flow")

    results = []

    try:
        # Create test directory
        test_dir = Path("/tmp/airels_test")
        test_dir.mkdir(exist_ok=True)

        # Create test video
        test_video = test_dir / "test_video.mp4"
        with open(test_video, 'wb') as f:
            f.write(b'test video content' * 100)

        # Import modules
        from integration.data_models import UploadOptions
        from integration.mock_uploader import MockInstagramUploader
        from integration.pipeline_bridge import PipelineBridge
        from job_queue.job_manager import JobManager, JobPriority

        # Setup pipeline
        uploader = MockInstagramUploader(success_rate=0.9, average_delay_seconds=0.2)
        pipeline = PipelineBridge(uploader)

        # Setup job manager
        job_manager = JobManager(
            storage_path=test_dir / "test_jobs.db",
            max_workers=2,
            poll_interval=0.2,
            auto_start=False
        )

        # Create upload handler
        async def upload_handler(job_data):
            qwen_output = job_data.get('qwen_output', {})
            options = UploadOptions.from_dict(job_data.get('options', {}))
            result = await pipeline.process_and_upload_with_retry(qwen_output, options)
            return {
                'success': result.successful,
                'status': result.status.value,
                'media_id': result.media_id,
                'duration': result.total_duration_seconds
            }

        job_manager.register_handler("instagram_upload", upload_handler)

        # Start job manager
        await job_manager.start()

        # Submit multiple jobs
        job_ids = []
        for i in range(3):
            job_data = {
                "qwen_output": {
                    "final_video_path": str(test_video),
                    "caption": f"Test job {i+1} #airels #testing",
                    "hashtags": ["#airels", "#testing", f"#job{i+1}"],
                    "topic": f"Test Topic {i+1}",
                },
                "options": {
                    "max_retries": 2,
                    "retry_delay_seconds": 1,
                    "validate_video": False,
                }
            }

            priority = JobPriority.HIGH if i == 0 else JobPriority.NORMAL
            job_id = await job_manager.submit_job(
                job_type="instagram_upload",
                data=job_data,
                priority=priority,
                metadata={"test_id": i, "video": "test_video.mp4"}
            )
            job_ids.append(job_id)
            print(f"  Submitted job {i+1}: {job_id[:8]}...")

        # Wait for jobs to process
        print("  Waiting for jobs to complete...")
        await asyncio.sleep(3)

        # Check results
        completed = 0
        for job_id in job_ids:
            status = await job_manager.get_job_status(job_id)
            if status and status['status'] == 'completed':
                completed += 1

        print(f"  Completed: {completed}/{len(job_ids)} jobs")
        assert completed > 0  # At least some should complete
        results.append(("Job processing", True))

        # Get queue stats
        stats = await job_manager.get_queue_stats()
        print(f"  Queue stats: {stats['total_jobs']} total jobs")
        results.append(("Queue statistics", True))

        # Stop job manager
        await job_manager.stop()
        results.append(("System cleanup", True))

        # Cleanup
        if test_video.exists():
            test_video.unlink()
        if (test_dir / "test_jobs.db").exists():
            (test_dir / "test_jobs.db").unlink()
        test_dir.rmdir()

    except Exception as e:
        results.append(("End-to-end flow tests", False, f"Error: {type(e).__name__}: {e}"))

    # Print results
    for test_name, success, *msg in results:
        print_result(test_name, success, msg[0] if msg else "")

    return all(success for success, *_ in results)

async def test_imports_and_dependencies():
    """Test that all imports work correctly."""
    print_header("TEST 5: Imports & Dependencies")

    results = []

    # Test critical imports
    import_tests = [
        ("integration.data_models", ["VideoMetadata", "UploadResult", "UploadStatus", "UploadOptions"]),
        ("integration.metadata_adapter", ["adapt_qwen_to_upload", "validate_metadata"]),
        ("integration.pipeline_bridge", ["PipelineBridge", "InstagramUploader"]),
        ("integration.mock_uploader", ["MockInstagramUploader"]),
        ("integration.playwright_uploader", ["PlaywrightUploader"]),
        ("job_queue.job_manager", ["JobManager", "Job", "JobStatus", "JobPriority"]),
        ("monitoring.dashboard", ["MonitoringDashboard", "SystemMetrics"]),
    ]

    for module_name, expected_imports in import_tests:
        try:
            module = __import__(module_name, fromlist=expected_imports)

            missing = []
            for import_name in expected_imports:
                if not hasattr(module, import_name):
                    missing.append(import_name)

            if missing:
                results.append((module_name, False, f"Missing: {', '.join(missing)}"))
            else:
                results.append((module_name, True, "OK"))

        except ImportError as e:
            results.append((module_name, False, f"ImportError: {e}"))
        except Exception as e:
            results.append((module_name, False, f"Error: {type(e).__name__}: {e}"))

    # Print results
    for test_name, success, *msg in results:
        print_result(test_name, success, msg[0] if msg else "")

    return all(success for success, *_ in results)

async def main():
    """Run all tests."""
    print("🚀 AIReels Sprint 3 - Comprehensive Test Suite")
    print("=" * 70)
    print("Testing all components of the pipeline...\n")

    # Run tests
    tests = [
        ("Imports & Dependencies", test_imports_and_dependencies),
        ("Integration Module", test_integration_module),
        ("Job Queue System", test_job_queue_system),
        ("Monitoring Dashboard", test_monitoring_dashboard),
        ("End-to-End Flow", test_end_to_end_flow),
    ]

    results = []
    all_passed = True

    for test_name, test_func in tests:
        try:
            passed = await test_func()
            results.append((test_name, passed))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {type(e).__name__}: {e}")
            results.append((test_name, False))
            all_passed = False

    # Print summary
    print_header("TEST SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\n📊 Results: {passed_count}/{total_count} tests passed")
    print(f"📈 Success rate: {passed_count/total_count*100:.1f}%")

    for test_name, passed in results:
        emoji = "✅" if passed else "❌"
        print(f"{emoji} {test_name}")

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The AIReels pipeline is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} tests failed")
        print("   Check the errors above and fix before deployment.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        sys.exit(1)
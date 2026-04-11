#!/usr/bin/env python3
"""
Example of using the job queue system with Instagram upload pipeline.

This example shows how to:
1. Create a JobManager for batch Instagram uploads
2. Register an Instagram upload handler
3. Submit multiple upload jobs
4. Monitor job progress
5. Handle retries and failures

Created by: Sam Lead Developer
Date: 2026-04-11
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def create_test_video_files(count: int = 3):
    """Create test video files for the example."""
    videos_dir = Path("/tmp/aireels_example_videos")
    videos_dir.mkdir(exist_ok=True)

    video_paths = []
    for i in range(count):
        video_path = videos_dir / f"test_video_{i+1}.mp4"

        # Create a minimal MP4-like file
        with open(video_path, 'wb') as f:
            f.write(b'ftypmp42')  # MP4 header
            f.write(b'\x00\x00\x00\x18')
            f.write(b'mp42isom')
            f.write(b'x' * 10240)  # 10KB of dummy data

        video_paths.append(str(video_path))
        print(f"  Created: {video_path.name}")

    return video_paths

async def main():
    """Run the queue system example."""
    print("🚀 Instagram Upload Queue System Example")
    print("=" * 70)

    try:
        # Import required modules
        from job_queue.job_manager import JobManager, JobPriority, create_instagram_upload_handler
        from integration.pipeline_bridge import PipelineBridge
        from integration.mock_uploader import MockInstagramUploader
        from integration.data_models import UploadOptions

        print("\n📦 Step 1: Creating test video files...")
        video_paths = create_test_video_files(3)
        print(f"✅ Created {len(video_paths)} test video files")

        print("\n🤖 Step 2: Setting up pipeline with mock uploader...")
        # Use mock uploader for this example (no real browser/API needed)
        uploader = MockInstagramUploader(success_rate=0.8, average_delay_seconds=0.5)
        pipeline = PipelineBridge(uploader)

        print("\n📊 Step 3: Creating job manager with persistence...")
        # Create data directory
        data_dir = Path("./data/examples")
        data_dir.mkdir(parents=True, exist_ok=True)

        job_manager = JobManager(
            storage_path=data_dir / "instagram_jobs.db",
            max_workers=2,  # Process 2 uploads concurrently
            poll_interval=0.5,  # Check for new jobs every 0.5 seconds
            auto_start=False  # We'll start manually
        )

        print("\n🔧 Step 4: Creating Instagram upload handler...")
        # Create handler that uses our pipeline
        upload_handler = await create_instagram_upload_handler(pipeline)
        job_manager.register_handler("instagram_upload", upload_handler)

        print("\n▶️  Step 5: Starting job manager...")
        await job_manager.start()

        print("\n📨 Step 6: Submitting upload jobs...")
        job_ids = []

        # Submit jobs with different priorities
        priorities = [
            (JobPriority.HIGH, "Urgent promotional content"),
            (JobPriority.NORMAL, "Regular content update"),
            (JobPriority.LOW, "Backlog content"),
        ]

        for i, (priority, description) in enumerate(priorities):
            if i >= len(video_paths):
                break

            # Create job data (mock qwen-poc output)
            job_data = {
                "qwen_output": {
                    "final_video_path": video_paths[i],
                    "caption": f"{description} - Example video #{i+1} #aireels #demo",
                    "hashtags": ["#aireels", "#demo", "#automation", "#example"],
                    "topic": f"Example Topic {i+1}",
                    "emotion": "excited" if i == 0 else "neutral",
                    "cta": "Like and follow for more!",
                    "on_screen_text": f"Example {i+1}",
                },
                "options": {
                    "max_retries": 2,
                    "retry_delay_seconds": 2,
                    "validate_video": False,  # Disable for example
                },
                "enrich_with_ai": False,
            }

            # Submit job
            job_id = await job_manager.submit_job(
                job_type="instagram_upload",
                data=job_data,
                priority=priority,
                metadata={
                    "description": description,
                    "video_index": i,
                    "video_file": Path(video_paths[i]).name,
                    "submitted_at": datetime.now().isoformat(),
                }
            )

            job_ids.append((job_id, priority, description))
            print(f"  Submitted: {job_id} ({priority.name} - {description})")

        print("\n⏳ Step 7: Monitoring job progress...")
        print("   (Jobs will process with mock uploader - 80% success rate)")

        # Monitor for 20 seconds or until all jobs are done
        start_time = datetime.now()
        completed_jobs = set()

        while (datetime.now() - start_time).total_seconds() < 20:
            await asyncio.sleep(2)

            # Get current stats
            stats = await job_manager.get_queue_stats()
            pending = stats['by_status'].get('pending', 0)
            processing = stats['by_status'].get('processing', 0)
            completed = stats['by_status'].get('completed', 0)
            failed = stats['by_status'].get('failed', 0)

            print(f"\n  📊 Current status: P={pending}, R={processing}, C={completed}, F={failed}")

            # Check individual job status
            print("  📋 Job details:")
            for job_id, priority, description in job_ids:
                if job_id in completed_jobs:
                    continue

                status_data = await job_manager.get_job_status(job_id)
                if status_data:
                    status = status_data['status']
                    attempts = status_data['attempts']
                    error = status_data.get('last_error', 'None')

                    if status in ['completed', 'failed', 'cancelled']:
                        completed_jobs.add(job_id)
                        result_symbol = '✅' if status == 'completed' else '❌'
                    else:
                        result_symbol = '🔄'

                    print(f"    {result_symbol} {job_id[:8]}...: {status} (attempts: {attempts})")

                    if error and error != 'None':
                        print(f"        Error: {error[:60]}...")

            # Check if all jobs are done
            if len(completed_jobs) == len(job_ids):
                print("\n  🎉 All jobs completed!")
                break

        print("\n📈 Step 8: Final statistics...")
        final_stats = await job_manager.get_queue_stats()

        print(f"  Total jobs: {final_stats['total_jobs']}")
        print(f"  By status:")
        for status, count in final_stats['by_status'].items():
            print(f"    {status}: {count}")

        print(f"  By priority:")
        for priority_val, count in final_stats['by_priority'].items():
            priority_name = JobPriority(priority_val).name
            print(f"    {priority_name}: {count}")

        print("\n🛑 Step 9: Stopping job manager...")
        await job_manager.stop()

        print("\n✨ Example completed successfully!")
        print("\n📝 Key features demonstrated:")
        print("   ✅ Priority-based job queue")
        print("   ✅ Concurrent processing (2 workers)")
        print("   ✅ Automatic retry on failure")
        print("   ✅ Persistent storage (SQLite)")
        print("   ✅ Real-time monitoring")
        print("   ✅ Integration with Instagram pipeline")

        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure all required modules are available")
        return False
    except Exception as e:
        print(f"\n❌ Error running example: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
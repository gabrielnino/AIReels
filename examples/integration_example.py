#!/usr/bin/env python3
"""
Example usage of the integration module.

This script demonstrates how to use the PipelineBridge with mock uploaders
to simulate the complete flow from qwen-poc output to Instagram upload.

Created by: Sam Lead Developer
Date: 2026-04-08
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from integration import (
    PipelineBridge,
    MockInstagramUploader,
    AlwaysSuccessUploader,
    AlwaysFailureUploader,
    FlakyUploader,
    UploadOptions,
)


def setup_logging():
    """Configure logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def create_mock_qwen_output(include_test_video: bool = False) -> dict:
    """
    Create a mock qwen-poc output dictionary for testing.

    This simulates the output from run_content_engine() in qwen-poc/pipeline.py

    Args:
        include_test_video: If True, use a test video path that exists
    """
    # Use a test video if available, otherwise use dummy path but skip validation
    if include_test_video:
        # Check for test videos in the project
        test_video_path = "/home/luis/code/AIReels/instagram-upload/videos/test_video.mp4"
        if os.path.exists(test_video_path):
            final_video_path = test_video_path
        else:
            # Create a dummy file for testing
            dummy_path = "/tmp/test_integration_video.mp4"
            if not os.path.exists(dummy_path):
                # Create empty file for testing
                with open(dummy_path, 'wb') as f:
                    f.write(b'dummy video content')
            final_video_path = dummy_path
    else:
        # Use dummy path but we'll disable file validation in examples
        final_video_path = "/tmp/generated/final_video_with_watermark.mp4"

    return {
        "topic": "The Future of AI in Content Creation",
        "emotion": "inspiring",
        "base_prompt": "futuristic AI creating digital art, neon lights, cyberpunk aesthetic",
        "style_anchor": "cyberpunk digital art",
        "silent_video_path": "/tmp/generated/silent_video.mp4",
        "audio_prompt": "uplifting electronic music with futuristic sounds",
        "video_with_audio_path": "/tmp/generated/video_with_audio.mp4",
        "final_video_path": final_video_path,
        "cta": "What AI tool are you most excited about? Comment below!",
        "on_screen_text": "AI is revolutionizing how we create content",
        "caption": "The future of content creation is here! AI tools are changing how we produce videos, write copy, and engage audiences. What do you think about this shift?",
        "hashtags": ["ai", "future", "contentcreation", "digitaltransformation"],
        "location": "San Francisco, California",
    }


async def example_basic_upload():
    """Example 1: Basic upload with mock uploader."""
    logger = setup_logging()
    logger.info("=== Example 1: Basic Upload ===")

    # Create mock uploader with 80% success rate
    uploader = MockInstagramUploader(
        success_rate=0.8,
        average_delay_seconds=1.0,  # Faster for demo
        delay_variation=0.5,
        simulate_validation=True
    )

    # Create pipeline bridge with validation disabled for file existence
    options = UploadOptions(
        validate_video=False,  # Disable file validation for demo
        validate_metadata=True,
        enable_debug_logging=True
    )

    bridge = PipelineBridge(uploader, options)

    # Create mock qwen output with test video
    qwen_output = create_mock_qwen_output(include_test_video=True)

    # Process and upload
    logger.info("Processing and uploading...")
    result = await bridge.process_and_upload(qwen_output, options)

    # Display results
    logger.info(f"Upload result: {result.status.value}")
    if result.media_id:
        logger.info(f"Media ID: {result.media_id}")
    logger.info(f"Duration: {result.total_duration_seconds:.1f}s")

    # Show uploader statistics
    stats = uploader.get_uploader_info()["statistics"]
    logger.info(f"Uploader stats: {stats}")

    return result


async def example_upload_with_retry():
    """Example 2: Upload with automatic retry logic."""
    logger = setup_logging()
    logger.info("\n=== Example 2: Upload with Retry ===")

    # Create uploader with low success rate to trigger retries
    uploader = MockInstagramUploader(
        success_rate=0.3,  # 30% success rate
        average_delay_seconds=1.0,
        delay_variation=0.5,
        simulate_validation=True
    )

    # Configure retry options
    options = UploadOptions(
        max_retries=3,
        retry_delay_seconds=2,
        validate_metadata=True,
        enable_debug_logging=True
    )

    # Create pipeline bridge with retry options
    bridge = PipelineBridge(uploader, options)

    # Create mock qwen output
    qwen_output = create_mock_qwen_output()

    # Process and upload with retry
    logger.info("Processing and uploading with retry...")
    result = await bridge.process_and_upload_with_retry(qwen_output)

    # Display results
    logger.info(f"Final result: {result.status.value}")
    logger.info(f"Retry count: {result.retry_count}")
    if result.error_message:
        logger.info(f"Error: {result.error_message}")

    return result


async def example_different_uploaders():
    """Example 3: Testing different uploader types."""
    logger = setup_logging()
    logger.info("\n=== Example 3: Different Uploader Types ===")

    # Test different uploader configurations
    uploaders = [
        ("Always Success", AlwaysSuccessUploader(delay_seconds=1.5)),
        ("Always Failure", AlwaysFailureUploader(delay_seconds=1.0)),
        ("Flaky (3 successes then 2 failures)", FlakyUploader(
            initial_success=True,
            failure_after_successes=3,
            recovery_after_failures=2,
            delay_seconds=2.0
        )),
    ]

    results = []
    qwen_output = create_mock_qwen_output()

    for name, uploader in uploaders:
        logger.info(f"\n--- Testing: {name} ---")

        bridge = PipelineBridge(uploader)
        result = await bridge.process_and_upload(qwen_output)

        logger.info(f"Result: {result.status.value}")
        if result.media_id:
            logger.info(f"Media ID: {result.media_id}")

        results.append((name, result))

    return results


async def example_bridge_information():
    """Example 4: Getting bridge and uploader information."""
    logger = setup_logging()
    logger.info("\n=== Example 4: Bridge Information ===")

    # Create uploader and bridge
    uploader = MockInstagramUploader()
    bridge = PipelineBridge(uploader)

    # Get uploader info
    uploader_info = uploader.get_uploader_info()
    logger.info("Uploader Information:")
    logger.info(f"  Type: {uploader_info['type']}")
    logger.info(f"  Name: {uploader_info['name']}")
    logger.info(f"  Success Rate: {uploader_info['configuration']['success_rate']}")

    # Get bridge info
    bridge_info = bridge.get_bridge_info()
    logger.info("\nBridge Information:")
    logger.info(f"  Version: {bridge_info['bridge_version']}")
    logger.info(f"  Uploader: {bridge_info['uploader']['name']}")
    logger.info(f"  Capabilities: {list(bridge_info['capabilities'].keys())}")

    return uploader_info, bridge_info


async def main():
    """Run all examples."""
    print("🚀 Integration Module Examples")
    print("=" * 50)

    try:
        # Run examples
        await example_basic_upload()
        await example_upload_with_retry()
        await example_different_uploaders()
        await example_bridge_information()

        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        print("\nNext steps:")
        print("1. Replace MockInstagramUploader with real implementation")
        print("2. Connect to actual qwen-poc pipeline output")
        print("3. Configure for production use")

    except Exception as e:
        print(f"\n❌ Error in examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    # Run the async examples
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
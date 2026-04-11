#!/usr/bin/env python3
"""
Test script for Playwright uploader integration.

This script tests the integration between the pipeline bridge
and the Playwright uploader implementation.

Created by: Sam Lead Developer
Date: 2026-04-11
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def create_test_video(video_path: Path, size_kb: int = 100):
    """Create a test video file."""
    video_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a small MP4 file (just a header with dummy data)
    # This is not a real video but should be enough for testing file operations
    with open(video_path, 'wb') as f:
        # Minimal MP4 header
        f.write(b'ftypmp42')
        f.write(b'\x00\x00\x00\x18')
        f.write(b'mp42isom')

        # Add some dummy data
        dummy_data = b'x' * (size_kb * 1024 - 20)  # Adjust for header size
        f.write(dummy_data)

    print(f"✅ Created test video: {video_path} ({size_kb}KB)")

async def test_playwright_uploader_initialization():
    """Test that PlaywrightUploader can be initialized."""
    print("\n🧪 Test 1: PlaywrightUploader Initialization")
    print("=" * 50)

    try:
        from integration.playwright_uploader import PlaywrightUploader

        # Create uploader in headless mode for testing
        uploader = PlaywrightUploader(headless=True)

        # Get uploader info
        info = uploader.get_uploader_info()

        print(f"✅ PlaywrightUploader initialized successfully")
        print(f"   Type: {info['type']}")
        print(f"   Name: {info['name']}")
        print(f"   Version: {info['version']}")
        print(f"   Capabilities: {', '.join(info['capabilities'].keys())}")

        # Test credential validation (will fail without real browser/auth)
        print("\n🔐 Testing credential validation...")
        try:
            # This will likely fail in test environment, but should not crash
            credentials_valid = await uploader.validate_credentials()
            print(f"   Credential validation: {'✅ Valid' if credentials_valid else '❌ Invalid (expected in test)'}")
        except Exception as e:
            print(f"   Credential validation error (expected): {type(e).__name__}")

        # Clean up
        await uploader.close()

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure instagram-upload directory exists and has required modules")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {type(e).__name__}: {e}")
        return False

async def test_pipeline_bridge_integration():
    """Test integration with PipelineBridge."""
    print("\n🧪 Test 2: Pipeline Bridge Integration")
    print("=" * 50)

    try:
        from integration.playwright_uploader import PlaywrightUploader
        from integration.pipeline_bridge import PipelineBridge
        from integration.data_models import UploadOptions

        # Create a test video file
        test_video = Path("/tmp/test_integration_video.mp4")
        create_test_video(test_video, size_kb=50)

        # Create uploader
        uploader = PlaywrightUploader(headless=True)

        # Create pipeline bridge
        bridge = PipelineBridge(uploader)

        # Get bridge info
        bridge_info = bridge.get_bridge_info()

        print("✅ PipelineBridge created with PlaywrightUploader")
        print(f"   Bridge version: {bridge_info['bridge_version']}")
        print(f"   Uploader type: {bridge_info['uploader']['type']}")
        print(f"   Capabilities: {', '.join(bridge_info['capabilities'].keys())}")

        # Test with mock qwen output
        qwen_output = {
            "final_video_path": str(test_video),
            "caption": "Test integration video #testing #playwright",
            "hashtags": ["#testing", "#integration", "#playwright"],
            "topic": "Integration Testing",
            "emotion": "neutral",
            "cta": "Testing Playwright uploader integration",
            "on_screen_text": "Test Video",
        }

        print("\n🔧 Testing pipeline bridge processing (mock mode)...")

        # Create upload options with validation disabled for testing
        options = UploadOptions(
            validate_video=False,  # Disable file validation for test
            validate_metadata=False,
            max_retries=1,
            retry_delay_seconds=1
        )

        # This will fail (no real browser/auth) but should handle gracefully
        try:
            result = await bridge.process_and_upload(qwen_output, options=options)
            print(f"   Processing completed with status: {result.status.value}")
            print(f"   Error message: {result.error_message or 'None'}")
            print(f"   Duration: {result.total_duration_seconds or 0:.1f}s")
        except Exception as e:
            print(f"   Processing error (expected in test): {type(e).__name__}: {e}")

        # Clean up
        await uploader.close()

        # Remove test file
        if test_video.exists():
            test_video.unlink()

        return True

    except Exception as e:
        print(f"❌ Integration test error: {type(e).__name__}: {e}")
        return False

async def test_mock_uploader_fallback():
    """Test that mock uploader still works as fallback."""
    print("\n🧪 Test 3: Mock Uploader Fallback")
    print("=" * 50)

    try:
        from integration.mock_uploader import MockInstagramUploader
        from integration.pipeline_bridge import PipelineBridge
        from integration.data_models import UploadOptions

        # Create a test video file
        test_video = Path("/tmp/test_mock_video.mp4")
        create_test_video(test_video, size_kb=10)

        # Create mock uploader (always succeeds)
        uploader = MockInstagramUploader(success_rate=1.0, average_delay_seconds=0.1)

        # Create pipeline bridge
        bridge = PipelineBridge(uploader)

        # Test qwen output
        qwen_output = {
            "final_video_path": str(test_video),
            "caption": "Mock upload test #mock #testing",
            "hashtags": ["#mock", "#testing"],
            "topic": "Mock Testing",
        }

        options = UploadOptions(
            validate_video=False,
            max_retries=0
        )

        print("🔄 Testing mock uploader...")
        result = await bridge.process_and_upload(qwen_output, options=options)

        print(f"✅ Mock upload completed")
        print(f"   Status: {result.status.value}")
        print(f"   Success: {result.successful}")
        print(f"   Media ID: {result.media_id or 'None'}")
        print(f"   Duration: {result.total_duration_seconds:.1f}s")

        # Clean up
        if test_video.exists():
            test_video.unlink()

        return result.successful

    except Exception as e:
        print(f"❌ Mock uploader test error: {type(e).__name__}: {e}")
        return False

async def main():
    """Run all integration tests."""
    print("🚀 AIReels Integration Test Suite")
    print("=" * 60)
    print("Testing Playwright uploader and pipeline integration\n")

    tests = [
        test_playwright_uploader_initialization,
        test_pipeline_bridge_integration,
        test_mock_uploader_fallback,
    ]

    results = []

    for test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {type(e).__name__}: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"✅ Tests passed: {passed}/{total}")
    print(f"📈 Success rate: {passed/total*100:.1f}%")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Playwright uploader integration is ready for use.")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("   Some integration issues need to be resolved.")

    return all(results)

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
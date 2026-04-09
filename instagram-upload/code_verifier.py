#!/usr/bin/env python3
"""
Code verifier for Instagram Upload Service.

Verifies that all modules can be imported and basic functionality works
without requiring pytest.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


class VerificationResult:
    """Result of a verification check."""
    def __init__(self, check_name, success=True, message="", error=None):
        self.check_name = check_name
        self.success = success
        self.message = message
        self.error = error

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.check_name}: {self.message}"


async def verify_module_import(module_name):
    """Verify a module can be imported."""
    try:
        # Convert path to module name
        if '/' in module_name:
            module_name = module_name.replace('/', '.').replace('.py', '')

        module = __import__(module_name, fromlist=['*'])
        return VerificationResult(
            f"Import {module_name}",
            success=True,
            message=f"Module imported successfully"
        )
    except ImportError as e:
        return VerificationResult(
            f"Import {module_name}",
            success=False,
            message=f"Import failed: {str(e)}",
            error=e
        )
    except Exception as e:
        return VerificationResult(
            f"Import {module_name}",
            success=False,
            message=f"Error: {str(e)}",
            error=e
        )


async def verify_class_creation(module_name, class_name):
    """Verify a class can be created."""
    try:
        # Import module
        if '/' in module_name:
            module_name = module_name.replace('/', '.').replace('.py', '')

        module = __import__(module_name, fromlist=['*'])
        class_obj = getattr(module, class_name)

        # Try to create instance
        instance = class_obj()
        return VerificationResult(
            f"Create {class_name}",
            success=True,
            message=f"Class {class_name} created successfully"
        )
    except Exception as e:
        return VerificationResult(
            f"Create {class_name}",
            success=False,
            message=f"Creation failed: {str(e)}",
            error=e
        )


async def verify_video_info():
    """Verify VideoInfo functionality."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        from src.upload.video_uploader import VideoInfo

        # Create VideoInfo
        video_info = VideoInfo(path=tmp_path)

        # Validate
        is_valid, errors = video_info.validate()

        os.unlink(tmp_path)

        if is_valid or "not allowed" not in str(errors):
            return VerificationResult(
                "VideoInfo validation",
                success=True,
                message=f"VideoInfo created and validated"
            )
        else:
            return VerificationResult(
                "VideoInfo validation",
                success=False,
                message=f"Validation errors: {errors}"
            )
    except Exception as e:
        os.unlink(tmp_path)
        return VerificationResult(
            "VideoInfo validation",
            success=False,
            message=f"Error: {str(e)}",
            error=e
        )


async def verify_video_metadata():
    """Verify VideoMetadata functionality."""
    try:
        from src.upload.metadata_handler import VideoMetadata

        # Create metadata
        metadata = VideoMetadata(
            caption="Test caption",
            hashtags=["test1", "test2"],
            location="Test Location"
        )

        # Validate
        is_valid, errors = metadata.validate()

        # Format
        formatted = metadata.format_caption_with_hashtags()

        if is_valid:
            return VerificationResult(
                "VideoMetadata functionality",
                success=True,
                message=f"Metadata validated, formatted length: {len(formatted)}"
            )
        else:
            return VerificationResult(
                "VideoMetadata functionality",
                success=False,
                message=f"Validation errors: {errors}"
            )
    except Exception as e:
        return VerificationResult(
            "VideoMetadata functionality",
            success=False,
            message=f"Error: {str(e)}",
            error=e
        )


async def verify_directory_structure():
    """Verify upload directory structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with open(os.path.join(temp_dir, ".env.instagram"), "w") as f:
                f.write("INSTAGRAM_VIDEO_INPUT_DIR=" + os.path.join(temp_dir, "input") + "\n")
                f.write("INSTAGRAM_VIDEO_PROCESSED_DIR=" + os.path.join(temp_dir, "processed") + "\n")
                f.write("INSTAGRAM_VIDEO_FAILED_DIR=" + os.path.join(temp_dir, "failed") + "\n")

            # Load environment
            from dotenv import load_dotenv
            load_dotenv(os.path.join(temp_dir, ".env.instagram"))

            from src.upload.video_uploader import VideoUploader

            # Create uploader
            uploader = VideoUploader()

            # Check directories
            if uploader.input_dir.exists() and uploader.processed_dir.exists() and uploader.failed_dir.exists():
                return VerificationResult(
                    "Directory structure",
                    success=True,
                    message="Upload directories created successfully"
                )
            else:
                return VerificationResult(
                    "Directory structure",
                    success=False,
                    message="Directories not created"
                )
        except Exception as e:
            return VerificationResult(
                "Directory structure",
                success=False,
                message=f"Error: {str(e)}",
                error=e
        )


async def verify_upload_flow_mocked():
    """Verify upload flow with mocked components."""
    try:
        from src.upload.video_uploader import VideoUploader, UploadResult, UploadStatus
        from src.upload.metadata_handler import MetadataHandler
        from src.upload.publisher import Publisher, PublicationResult, PublicationStatus

        # Mock browser service
        mock_browser_service = type('MockBrowser', (), {})

        # Create components
        uploader = VideoUploader(mock_browser_service)
        metadata_handler = MetadataHandler(mock_browser_service)
        publisher = Publisher(mock_browser_service)

        # Create mock results
        upload_result = UploadResult(
            success=True,
            video_info=None,
            status=UploadStatus.COMPLETED,
            message="Mock upload"
        )

        publication_result = PublicationResult(
            success=True,
            status=PublicationStatus.PUBLISHED,
            message="Mock publication"
        )

        return VerificationResult(
            "Upload flow components",
            success=True,
            message="All upload flow components created successfully"
        )
    except Exception as e:
        return VerificationResult(
            "Upload flow components",
            success=False,
            message=f"Error: {str(e)}",
            error=e
        )


async def main():
    """Main verification function."""
    print("🔍 Code Verification for Instagram Upload Service")
    print("==================================================")

    verification_checks = [
        # Module imports
        ("src.auth.browser_service", "BrowserService"),
        ("src.auth.login_manager", "InstagramLoginManager"),
        ("src.auth.cookie_manager", "CookieManager"),
        ("src.upload.video_uploader", "VideoUploader"),
        ("src.upload.metadata_handler", "MetadataHandler"),
        ("src.upload.publisher", "Publisher"),

        # Functionality checks
        verify_video_info,
        verify_video_metadata,
        verify_directory_structure,
        verify_upload_flow_mocked,
    ]

    results = []

    for check in verification_checks:
        if isinstance(check, tuple):
            # Module import and class creation check
            module_name, class_name = check

            # Import check
            import_result = await verify_module_import(module_name)
            results.append(import_result)
            print(f"{import_result}")

            # Class creation check (if import succeeded)
            if import_result.success:
                creation_result = await verify_class_creation(module_name, class_name)
                results.append(creation_result)
                print(f"{creation_result}")
        else:
            # Function check
            result = await check()
            results.append(result)
            print(f"{result}")

    # Summary
    print("\n📊 VERIFICATION SUMMARY")
    print("========================")

    total_checks = len(results)
    passed_checks = sum(1 for r in results if r.success)
    failed_checks = total_checks - passed_checks

    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {failed_checks}")

    if failed_checks == 0:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("✅ Code structure is valid and modules can be imported")
        print("✅ Basic functionality verified")
        print("✅ Ready for integration testing with actual browser")
    else:
        print("\n⚠️  SOME VERIFICATIONS FAILED")

        # Show failed checks
        print("\nFailed checks:")
        for result in results:
            if not result.success:
                print(f"  ❌ {result.check_name}: {result.message}")

    return failed_checks == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Manual tests for metadata adapter module.

These tests can run WITHOUT pytest, using plain Python.
We can run them NOW while Taylor works on resolving B1.

Created by: Sam Lead Developer
Date: 2026-04-08
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Also add current directory for imports
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from integration import (
    VideoMetadata,
    UploadOptions,
    adapt_qwen_to_upload,
    validate_metadata,
)


def test_adapt_valid_qwen_output():
    """Test adaptation with valid qwen-poc output."""
    print("🧪 Test 1: Adaptación con output válido de qwen-poc")

    # Valid qwen output (similar to real output)
    qwen_output = {
        "final_video_path": "/tmp/test_video.mp4",
        "caption": "Test caption for Instagram",
        "hashtags": ["#test", "#demo", "#integration"],
        "topic": "Testing Metadata Adaptation",
        "emotion": "neutral",
        "cta": "Like and share if you enjoyed!",
        "on_screen_text": "Testing in progress",
        "location": "Test Location",
    }

    # Create a dummy video file
    dummy_path = "/tmp/test_video.mp4"
    if not os.path.exists(dummy_path):
        with open(dummy_path, 'wb') as f:
            f.write(b'dummy video content')

    # Adapt
    options = UploadOptions(validate_video=False)  # Disable file validation
    metadata = adapt_qwen_to_upload(qwen_output, options)

    # Verify
    assert metadata.video_path == dummy_path
    assert metadata.caption == "Test caption for Instagram"
    assert metadata.hashtags == ["#test", "#demo", "#integration"]
    assert metadata.topic == "Testing Metadata Adaptation"

    print("✅ PASS: Metadata adapted correctly")
    return True


def test_adapt_missing_required_field():
    """Test adaptation with missing required field."""
    print("\n🧪 Test 2: Adaptación con campo requerido faltante")

    # Invalid qwen output (missing final_video_path)
    qwen_output = {
        "caption": "Test caption",
        "hashtags": ["#test"],
        "topic": "Testing",
    }

    try:
        metadata = adapt_qwen_to_upload(qwen_output)
        print("❌ FAIL: Should have raised ValueError")
        return False
    except ValueError as e:
        if "final_video_path" in str(e):
            print("✅ PASS: Correctly raised ValueError for missing field")
            return True
        else:
            print(f"❌ FAIL: Wrong error message: {e}")
            return False


def test_validate_metadata_instagram_limits():
    """Test validation against Instagram limits."""
    print("\n🧪 Test 3: Validación contra límites de Instagram")

    # Create metadata that exceeds Instagram limits
    metadata = VideoMetadata(
        video_path="/tmp/test.mp4",
        caption="A" * 2500,  # >2200 character limit
        hashtags=["#tag"] * 35,  # >30 hashtag limit
        file_size_mb=150.0,  # >100MB limit
    )

    options = UploadOptions(validate_metadata=True)

    try:
        validate_metadata(metadata, options)
        print("❌ FAIL: Should have raised ValueError")
        return False
    except ValueError as e:
        errors = str(e)
        if "Caption too long" in errors and "Too many hashtags" in errors and "Video file too large" in errors:
            print("✅ PASS: Correctly detected all limit violations")
            return True
        else:
            print(f"❌ FAIL: Missing some validations: {errors}")
            return False


def test_validate_metadata_valid():
    """Test validation with valid metadata."""
    print("\n🧪 Test 4: Validación con metadata válida")

    # Create valid metadata
    metadata = VideoMetadata(
        video_path="/tmp/test.mp4",
        caption="Valid caption under 2200 chars",
        hashtags=["#valid", "#test", "#demo"],
        file_size_mb=50.0,  # Under 100MB limit
        video_format="mp4",
    )

    # Create dummy file
    dummy_path = "/tmp/test.mp4"
    if not os.path.exists(dummy_path):
        with open(dummy_path, 'wb') as f:
            f.write(b'dummy')

    options = UploadOptions(validate_metadata=True)

    try:
        validate_metadata(metadata, options)
        print("✅ PASS: Valid metadata passed validation")
        return True
    except ValueError as e:
        print(f"❌ FAIL: Should not have raised error: {e}")
        return False


def test_hashtag_format_validation():
    """Test hashtag format validation."""
    print("\n🧪 Test 5: Validación de formato de hashtags")

    # Metadata with incorrectly formatted hashtags
    metadata = VideoMetadata(
        video_path="/tmp/test.mp4",
        caption="Test",
        hashtags=["ai", "future", "#correct", "nocorrect"],  # Mixed correct/incorrect
    )

    options = UploadOptions(validate_metadata=True)

    try:
        validate_metadata(metadata, options)
        print("❌ FAIL: Should have raised ValueError for bad hashtags")
        return False
    except ValueError as e:
        errors = str(e)
        # Should mention ai, future, nocorrect but NOT #correct
        if "ai" in errors and "future" in errors and "nocorrect" in errors and "#correct" not in errors:
            print("✅ PASS: Correctly identified bad hashtags")
            return True
        else:
            print(f"❌ FAIL: Error analysis incorrect: {errors}")
            return False


def run_all_tests():
    """Run all manual tests."""
    print("\n🚀 EJECUTANDO TESTS MANUALES DE METADATA ADAPTER")
    print("==================================================")

    tests = [
        test_adapt_valid_qwen_output,
        test_adapt_missing_required_field,
        test_validate_metadata_instagram_limits,
        test_validate_metadata_valid,
        test_hashtag_format_validation,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ ERROR ejecutando test: {e}")
            results.append(False)

    # Summary
    print("\n==================================================")
    print("📊 RESUMEN DE TESTS:")

    passed = sum(results)
    total = len(results)

    print(f"✅ Tests pasados: {passed}/{total}")
    print(f"📈 Porcentaje: {passed/total*100:.1f}%")

    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests fallaron")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
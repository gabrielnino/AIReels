#!/usr/bin/env python3
"""
Manual test runner for Instagram Upload Service tests.

Since pytest may not be available, this script runs tests manually
to verify functionality.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import sys
import os
import asyncio
import inspect
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


class TestResult:
    """Result of a test run."""
    def __init__(self, test_name, success=True, message="", error=None):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.error = error

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.test_name}: {self.message}"


async def run_async_test(test_func):
    """Run an async test function."""
    try:
        result = await test_func()
        return TestResult(test_func.__name__, success=True, message="Passed")
    except Exception as e:
        return TestResult(
            test_func.__name__,
            success=False,
            message=f"Failed: {str(e)}",
            error=e
        )


def run_sync_test(test_func):
    """Run a sync test function."""
    try:
        test_func()
        return TestResult(test_func.__name__, success=True, message="Passed")
    except Exception as e:
        return TestResult(
            test_func.__name__,
            success=False,
            message=f"Failed: {str(e)}",
            error=e
        )


def find_test_classes(module_path):
    """Find test classes in a module."""
    try:
        # Import module
        module_name = module_path.replace('/', '.').replace('.py', '')
        module = __import__(module_name, fromlist=['*'])

        test_classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name.startswith('Test'):
                test_classes.append((name, obj))

        return test_classes
    except Exception as e:
        print(f"⚠️  Could not import module {module_path}: {e}")
        return []


async def run_module_tests(module_path):
    """Run all tests in a module."""
    print(f"\n🧪 Running tests from: {module_path}")

    test_classes = find_test_classes(module_path)

    if not test_classes:
        print("   No test classes found")
        return []

    results = []

    for class_name, test_class in test_classes:
        print(f"\n   Class: {class_name}")

        # Find test methods
        test_methods = []
        for name, method in inspect.getmembers(test_class):
            if name.startswith('test_') and inspect.isfunction(method):
                test_methods.append((name, method))

        for method_name, test_method in test_methods:
            print(f"     Method: {method_name}")

            # Check if method is async
            if inspect.iscoroutinefunction(test_method):
                # Create instance and run async test
                instance = test_class()
                result = await run_async_test(test_method.__get__(instance, test_class))
                results.append(result)
                print(f"       {result}")
            else:
                # Create instance and run sync test
                instance = test_class()
                result = run_sync_test(test_method.__get__(instance, test_class))
                results.append(result)
                print(f"       {result}")

    return results


async def main():
    """Main test runner function."""
    print("🚀 Manual Test Runner for Instagram Upload Service")
    print("==================================================")

    test_modules = [
        "tests.unit.auth.test_login_manager",
        "tests.unit.auth.test_browser_service",
        "tests.unit.auth.test_cookie_manager",
        "tests.unit.upload.test_video_uploader",
        "tests.unit.upload.test_metadata_handler",
        "tests.unit.upload.test_publisher",
        "tests.integration.auth.test_auth_integration",
        "tests.integration.upload.test_upload_integration"
    ]

    all_results = []
    total_tests = 0
    passed_tests = 0

    for module in test_modules:
        module_results = await run_module_tests(module)
        all_results.extend(module_results)

        for result in module_results:
            total_tests += 1
            if result.success:
                passed_tests += 1

    # Summary
    print("\n📊 TEST SUMMARY")
    print("================")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if total_tests == passed_tests:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n💀 SOME TESTS FAILED")

        # Show failed tests
        print("\nFailed tests:")
        for result in all_results:
            if not result.success:
                print(f"  ❌ {result.test_name}: {result.message}")
                if result.error:
                    import traceback
                    print(f"     Error details: {traceback.format_exception_only(type(result.error), result.error)[0]}")

    return total_tests == passed_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test runner for Instagram Upload Service.

Created by: Taylor QA Engineer (QA Automation)
Date: 2026-04-08
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_unit_tests():
    """Run all unit tests."""
    print("🧪 Running unit tests...")
    print("=" * 50)

    test_dir = Path(__file__).parent / "tests" / "unit"

    # Run pytest on the unit test directory
    cmd = [sys.executable, "-m", "pytest", str(test_dir), "-v", "--tb=short"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0

def run_integration_tests():
    """Run all integration tests."""
    print("🔗 Running integration tests...")
    print("=" * 50)

    test_dir = Path(__file__).parent / "tests" / "integration"

    if not test_dir.exists() or not any(test_dir.iterdir()):
        print("No integration tests found.")
        return True

    # Run pytest on the integration test directory
    cmd = [sys.executable, "-m", "pytest", str(test_dir), "-v", "--tb=short"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0

def run_specific_test(test_path):
    """Run a specific test file."""
    print(f"🎯 Running specific test: {test_path}")
    print("=" * 50)

    cmd = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0

def calculate_coverage():
    """Calculate test coverage."""
    print("📊 Calculating test coverage...")
    print("=" * 50)

    src_dir = Path(__file__).parent / "src"

    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=" + str(src_dir),
        "--cov-report=term-missing",
        "--cov-report=html:coverage_html",
        "tests/unit",
        "-v"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Check if coverage meets minimum (80% for new code)
    if "TOTAL" in result.stdout:
        lines = result.stdout.split('\n')
        for line in lines:
            if "TOTAL" in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        coverage = float(parts[-1].replace('%', ''))
                        print(f"\n📈 Total coverage: {coverage:.1f}%")

                        if coverage >= 80:
                            print("✅ Coverage meets minimum requirement (80%)")
                        else:
                            print("❌ Coverage below minimum requirement (80%)")
                            return False
                    except:
                        pass

    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Run tests for Instagram Upload Service")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--coverage", action="store_true", help="Calculate test coverage")
    parser.add_argument("--test", type=str, help="Run specific test file")

    args = parser.parse_args()

    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))

    all_success = True

    if args.test:
        all_success = run_specific_test(args.test)
    elif args.unit:
        all_success = run_unit_tests()
    elif args.integration:
        all_success = run_integration_tests()
    elif args.coverage:
        all_success = calculate_coverage()
    else:
        # Run all tests by default
        print("🚀 Running all tests for Instagram Upload Service")
        print("=" * 50)

        unit_success = run_unit_tests()
        print("\n" + "=" * 50 + "\n")

        integration_success = run_integration_tests()
        print("\n" + "=" * 50 + "\n")

        coverage_success = calculate_coverage()

        all_success = unit_success and integration_success and coverage_success

    if all_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💀 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
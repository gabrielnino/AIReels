#!/usr/bin/env python3
"""
Coverage calculation script for qwen-poc services.

Calculates test coverage for all services in qwen-poc/service/ directory.
Generates individual and aggregate coverage reports.

Created by: Taylor QA Engineer
Date: 2026-04-09
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class QwenCoverageCalculator:
    """Calculate test coverage for qwen-poc services."""

    def __init__(self):
        self.base_dir = Path(__file__).parent / "qwen-poc"
        self.service_dir = self.base_dir / "service"
        self.tests_dir = self.base_dir / "tests"
        self.results = {}

    def get_all_services(self) -> List[str]:
        """Get list of all service files."""
        services = []
        for file in self.service_dir.glob("*.py"):
            if file.name != "__init__.py":
                services.append(file.name)
        return sorted(services)

    def find_test_file(self, service_name: str) -> Optional[Path]:
        """Find test file for a service if it exists."""
        service_base = service_name.replace(".py", "")

        # Check in tests/unit directory
        test_file = self.tests_dir / "unit" / f"test_{service_base}.py"
        if test_file.exists():
            return test_file

        # Check in tests directory
        test_file = self.tests_dir / f"test_{service_base}.py"
        if test_file.exists():
            return test_file

        return None

    def calculate_service_coverage(self, service_name: str) -> Dict:
        """Calculate coverage for a single service."""
        service_path = self.service_dir / service_name
        test_file = self.find_test_file(service_name)

        result = {
            "service": service_name,
            "has_tests": test_file is not None,
            "test_file": str(test_file) if test_file else None,
            "coverage": None,
            "lines_covered": None,
            "lines_total": None,
            "error": None
        }

        if not test_file:
            result["error"] = "No test file found"
            return result

        try:
            # Run pytest with coverage for this specific service
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_file),
                "--cov", str(service_path),
                "--cov-report", "json",
                "-q"
            ]

            # Run the command
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                timeout=30
            )

            # Check if coverage data was generated
            coverage_file = self.base_dir / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)

                # Extract coverage for this specific file
                files = coverage_data.get("files", {})
                service_key = str(service_path.relative_to(self.base_dir))

                if service_key in files:
                    file_data = files[service_key]
                    result["coverage"] = file_data.get("summary", {}).get("percent_covered", 0)
                    result["lines_covered"] = file_data.get("summary", {}).get("covered_lines", 0)
                    result["lines_total"] = file_data.get("summary", {}).get("num_statements", 0)

                # Clean up
                coverage_file.unlink(missing_ok=True)
            else:
                result["error"] = "No coverage data generated"

        except subprocess.TimeoutExpired:
            result["error"] = "Test execution timed out"
        except Exception as e:
            result["error"] = str(e)

        return result

    def calculate_aggregate_coverage(self) -> Dict:
        """Calculate aggregate coverage across all services."""
        total_lines = 0
        total_covered = 0
        services_with_tests = 0
        services_without_tests = 0

        for service_name, data in self.results.items():
            if data["lines_total"] and data["lines_covered"]:
                total_lines += data["lines_total"]
                total_covered += data["lines_covered"]
                services_with_tests += 1
            elif not data["has_tests"]:
                services_without_tests += 1

        aggregate_coverage = 0
        if total_lines > 0:
            aggregate_coverage = (total_covered / total_lines) * 100

        return {
            "aggregate_coverage": aggregate_coverage,
            "total_lines": total_lines,
            "total_covered": total_covered,
            "services_with_tests": services_with_tests,
            "services_without_tests": services_without_tests,
            "total_services": len(self.results)
        }

    def generate_report(self) -> str:
        """Generate markdown report of coverage results."""
        report = []
        report.append("# 📊 QWEN-POC COVERAGE REPORT")
        report.append(f"**Generated:** 2026-04-09")
        report.append(f"**Generated by:** Taylor QA Engineer")
        report.append("")

        # Summary section
        agg = self.calculate_aggregate_coverage()
        report.append("## 📈 SUMMARY")
        report.append("")
        report.append(f"**Total Services:** {agg['total_services']}")
        report.append(f"**Services with Tests:** {agg['services_with_tests']}")
        report.append(f"**Services without Tests:** {agg['services_without_tests']}")
        report.append(f"**Aggregate Coverage:** {agg['aggregate_coverage']:.1f}%")
        report.append(f"**Lines Covered:** {agg['total_covered']} / {agg['total_lines']}")
        report.append("")

        # Detailed results
        report.append("## 📋 DETAILED RESULTS BY SERVICE")
        report.append("")
        report.append("| Service | Has Tests | Coverage | Lines | Status |")
        report.append("|---------|-----------|----------|-------|--------|")

        for service_name, data in sorted(self.results.items()):
            if data["has_tests"] and data["coverage"] is not None:
                coverage_display = f"{data['coverage']:.1f}%"
                lines_display = f"{data['lines_covered']}/{data['lines_total']}"
                status = "✅" if data["coverage"] >= 80 else "⚠️"
            elif data["has_tests"]:
                coverage_display = "N/A"
                lines_display = "N/A"
                status = "❌"
            else:
                coverage_display = "No tests"
                lines_display = "N/A"
                status = "📝"

            report.append(f"| `{service_name}` | {'Yes' if data['has_tests'] else 'No'} | {coverage_display} | {lines_display} | {status} |")

        report.append("")

        # Recommendations
        report.append("## 🎯 RECOMMENDATIONS")
        report.append("")

        services_without_tests = [
            name for name, data in self.results.items()
            if not data["has_tests"] or data["error"]
        ]

        if services_without_tests:
            report.append("### **Services Needing Tests:**")
            for service in services_without_tests:
                data = self.results[service]
                if data["error"]:
                    report.append(f"- `{service}`: Error - {data['error']}")
                else:
                    report.append(f"- `{service}`: No test file found")
            report.append("")

        low_coverage = [
            (name, data["coverage"]) for name, data in self.results.items()
            if data["coverage"] is not None and data["coverage"] < 80
        ]

        if low_coverage:
            report.append("### **Services Needing More Coverage:**")
            for service, coverage in sorted(low_coverage, key=lambda x: x[1]):
                report.append(f"- `{service}`: {coverage:.1f}% (target: 80%)")
            report.append("")

        report.append("### **Next Steps:**")
        report.append("1. Implement tests for services without coverage")
        report.append("2. Increase coverage for services below 80%")
        report.append("3. Add integration tests for service interactions")
        report.append("4. Set up CI/CD with coverage requirements")
        report.append("")

        return "\n".join(report)

    def run(self):
        """Main execution method."""
        print("🔍 Calculating coverage for qwen-poc services...")
        print("=" * 60)

        services = self.get_all_services()
        print(f"Found {len(services)} services")

        for i, service in enumerate(services, 1):
            print(f"[{i}/{len(services)}] Calculating coverage for: {service}")
            self.results[service] = self.calculate_service_coverage(service)

        print("=" * 60)
        print("✅ Coverage calculation complete")

        # Generate and save report
        report = self.generate_report()
        report_path = self.base_dir.parent / "QWEN_COVERAGE_REPORT.md"

        with open(report_path, 'w') as f:
            f.write(report)

        print(f"📄 Report saved to: {report_path}")

        # Print summary
        agg = self.calculate_aggregate_coverage()
        print(f"\n📊 SUMMARY:")
        print(f"  Services with tests: {agg['services_with_tests']}/{agg['total_services']}")
        print(f"  Aggregate coverage: {agg['aggregate_coverage']:.1f}%")
        print(f"  Lines covered: {agg['total_covered']}/{agg['total_lines']}")

if __name__ == "__main__":
    calculator = QwenCoverageCalculator()
    calculator.run()
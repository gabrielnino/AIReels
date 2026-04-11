#!/usr/bin/env python3
"""
Fix Python import issues in the AIReels project.

This script fixes common import issues:
1. Relative imports in test files
2. Missing __init__.py files
3. Incorrect sys.path modifications
4. Module not found errors

Created by: Sam Lead Developer
Date: 2026-04-11
"""

import os
import re
import sys
from pathlib import Path
import subprocess

def find_python_files(root_dir):
    """Find all Python files in the project."""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip virtual environments and cache directories
        if any(skip in root for skip in ['venv', '__pycache__', '.pytest_cache', '.git']):
            continue

        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    return python_files

def analyze_imports(file_path):
    """Analyze import statements in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()

    issues = []

    # Check for problematic import patterns
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()

        # Check for imports from instagram_upload.src
        if 'instagram_upload.src.' in line:
            issues.append({
                'line': i,
                'issue': 'instagram_upload.src import',
                'fix': line.replace('instagram_upload.src.', 'src.')
            })

        # Check for absolute imports that should be relative
        elif 'from src.' in line and 'tests' in str(file_path):
            # Test files should use relative imports or add to sys.path
            issues.append({
                'line': i,
                'issue': 'Absolute import in test file',
                'fix': f'# TODO: Fix import - {line}'
            })

        # Check for missing sys.path modifications in test files
        elif 'tests' in str(file_path) and i == 1 and 'sys.path' not in content:
            issues.append({
                'line': 1,
                'issue': 'Test file missing sys.path setup',
                'fix': 'import sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
            })

    return issues

def fix_test_file_imports(file_path):
    """Fix imports in test files."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Add sys.path setup if missing
    if 'import sys' not in content and 'tests' in str(file_path):
        # Insert after shebang if present
        lines = content.split('\n')
        new_lines = []

        for i, line in enumerate(lines):
            new_lines.append(line)
            if i == 0 and (line.startswith('#!/') or line.startswith('#!')):
                # Add imports after shebang
                new_lines.append('')
                new_lines.append('import sys')
                new_lines.append('import os')
                new_lines.append('sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))')
                new_lines.append('')
            elif i == 0:
                # Add imports at the beginning
                new_lines.insert(0, 'import sys')
                new_lines.insert(1, 'import os')
                new_lines.insert(2, 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))')
                new_lines.insert(3, '')
                break

        content = '\n'.join(new_lines)

    # Fix instagram_upload.src imports
    content = content.replace('instagram_upload.src.', 'src.')

    # Fix other common issues
    content = content.replace('from integration import', 'from src.integration import')
    content = content.replace('import integration', 'import sys\nimport os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))\nfrom integration import')

    with open(file_path, 'w') as f:
        f.write(content)

    return True

def create_init_files():
    """Create missing __init__.py files."""
    directories = [
        Path('src'),
        Path('src/integration'),
        Path('src/job_queue'),
        Path('tests'),
        Path('tests/integration'),
        Path('examples'),
    ]

    for dir_path in directories:
        init_file = dir_path / '__init__.py'
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            with open(init_file, 'w') as f:
                f.write(f'# {dir_path.name} module\n')
                f.write(f'# Auto-generated on 2026-04-11\n')
                f.write(f'__version__ = "0.1.0"\n')
            print(f"✅ Created {init_file}")

def test_imports():
    """Test imports for common modules."""
    test_cases = [
        ('src.integration.data_models', ['VideoMetadata', 'UploadResult', 'UploadStatus', 'UploadOptions']),
        ('src.integration.metadata_adapter', ['adapt_qwen_to_upload', 'validate_metadata']),
        ('src.integration.pipeline_bridge', ['PipelineBridge', 'InstagramUploader']),
        ('src.integration.mock_uploader', ['MockInstagramUploader']),
        ('src.integration.playwright_uploader', ['PlaywrightUploader']),
        ('src.job_queue.job_manager', ['JobManager', 'Job', 'JobStatus', 'JobPriority']),
    ]

    results = []

    for module_name, expected_imports in test_cases:
        try:
            # Temporarily add src to path
            import sys
            sys.path.insert(0, str(Path.cwd()))

            module = __import__(module_name, fromlist=expected_imports)

            # Check each expected import
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

    return results

def create_requirements_file():
    """Create comprehensive requirements.txt file."""
    requirements = """# AIReels Project Requirements
# Generated: 2026-04-11

# Core dependencies
python-dotenv>=1.0.0

# Playwright for UI automation (Instagram upload)
playwright>=1.40.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Web framework (for dashboard)
Flask>=2.0.0

# Database (for job queue)
# Note: SQLite is included in Python standard library

# Development tools
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# Async utilities
aiohttp>=3.9.0

# Install Playwright browsers:
# playwright install chromium
# playwright install firefox
# playwright install webkit
"""

    with open('requirements.txt', 'w') as f:
        f.write(requirements)

    print("✅ Created requirements.txt")

def create_setup_py():
    """Create setup.py for proper package installation."""
    setup_content = """from setuptools import setup, find_packages

setup(
    name="airels",
    version="0.1.0",
    description="AI-powered Instagram Reels automation pipeline",
    author="AIReels Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-dotenv>=1.0.0",
        "playwright>=1.40.0",
        "Flask>=2.0.0",
        "aiohttp>=3.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    python_requires=">=3.8",
)
"""

    with open('setup.py', 'w') as f:
        f.write(setup_content)

    print("✅ Created setup.py")

def main():
    """Main function to fix all import issues."""
    print("🔧 FIXING PYTHON IMPORT ISSUES (B4)")
    print("=" * 60)

    root_dir = Path.cwd()

    # Step 1: Create __init__.py files
    print("\n📁 Step 1: Creating missing __init__.py files...")
    create_init_files()

    # Step 2: Analyze Python files
    print("\n🔍 Step 2: Analyzing Python files for import issues...")
    python_files = find_python_files(root_dir)

    total_issues = 0
    files_with_issues = []

    for file_path in python_files:
        issues = analyze_imports(file_path)
        if issues:
            total_issues += len(issues)
            files_with_issues.append((file_path, issues))
            print(f"  ⚠️  {file_path.relative_to(root_dir)}: {len(issues)} issues")

    # Step 3: Fix test files
    print(f"\n🔧 Step 3: Fixing import issues in {len(files_with_issues)} files...")
    fixed_count = 0

    for file_path, issues in files_with_issues:
        if 'test' in str(file_path).lower() or 'tests' in str(file_path):
            if fix_test_file_imports(file_path):
                fixed_count += 1
                print(f"  ✅ Fixed: {file_path.relative_to(root_dir)}")

    # Step 4: Create requirements and setup files
    print("\n📦 Step 4: Creating package configuration files...")
    create_requirements_file()
    create_setup_py()

    # Step 5: Test imports
    print("\n🧪 Step 5: Testing imports...")
    import_results = test_imports()

    successful = 0
    for module_name, success, message in import_results:
        if success:
            print(f"  ✅ {module_name}: {message}")
            successful += 1
        else:
            print(f"  ❌ {module_name}: {message}")

    # Step 6: Create a simple test script
    print("\n📝 Step 6: Creating import test script...")
    test_script = """#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.

Run with: python test_imports.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_import(module_name, imports=None):
    """Test importing a module."""
    try:
        if imports:
            module = __import__(module_name, fromlist=imports)
            for imp in imports:
                if not hasattr(module, imp):
                    return False, f"Missing {imp}"
        else:
            __import__(module_name)
        return True, "OK"
    except ImportError as e:
        return False, f"ImportError: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def main():
    """Test all critical imports."""
    print("🧪 Testing AIReels imports")
    print("=" * 50)

    tests = [
        ("integration.data_models", ["VideoMetadata", "UploadResult", "UploadStatus", "UploadOptions"]),
        ("integration.metadata_adapter", ["adapt_qwen_to_upload", "validate_metadata"]),
        ("integration.pipeline_bridge", ["PipelineBridge", "InstagramUploader"]),
        ("integration.mock_uploader", ["MockInstagramUploader"]),
        ("job_queue.job_manager", ["JobManager", "Job", "JobStatus", "JobPriority"]),
    ]

    all_ok = True
    for module_name, imports in tests:
        success, message = test_import(module_name, imports)
        status = "✅" if success else "❌"
        print(f"{status} {module_name}: {message}")
        if not success:
            all_ok = False

    print("=" * 50)
    if all_ok:
        print("🎉 All imports successful!")
        return 0
    else:
        print("⚠️  Some imports failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""

    with open('test_imports.py', 'w') as f:
        f.write(test_script)

    print("  ✅ Created test_imports.py")

    # Summary
    print("\n" + "=" * 60)
    print("📊 FIX SUMMARY")
    print("=" * 60)
    print(f"📁 Files analyzed: {len(python_files)}")
    print(f"⚠️  Files with issues: {len(files_with_issues)}")
    print(f"🔧 Files fixed: {fixed_count}")
    print(f"📦 Package files created: 2 (requirements.txt, setup.py)")
    print(f"🧪 Import tests: {successful}/{len(import_results)} successful")

    if successful == len(import_results):
        print("\n🎉 ALL IMPORT ISSUES RESOLVED!")
        print("   Run 'python test_imports.py' to verify")
    else:
        print(f"\n⚠️  {len(import_results) - successful} imports still failing")
        print("   Check the errors above and fix manually")

    print("\n📝 Next steps:")
    print("   1. Run: python test_imports.py")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Install Playwright browsers: playwright install chromium")
    print("   4. Run tests: python -m pytest tests/")

if __name__ == "__main__":
    main()
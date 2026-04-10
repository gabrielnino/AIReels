"""
Global pytest configuration for AIReels project.
"""
import os
import sys
from pathlib import Path

# Añadir proyecto al PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "instagram-upload"))
sys.path.insert(0, str(project_root / "qwen-poc"))

# Load test environment variables
test_env_path = project_root / ".env.test"
if test_env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(test_env_path)
    print(f"✅ Loaded test environment from: {test_env_path}")
else:
    print(f"⚠️  Test environment file not found: {test_env_path}")

# Pytest configuration
def pytest_configure(config):
    """Pytest configuration hook."""
    # Markers para tests
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (require external services)"
    )
    config.addinivalue_line(
        "markers",
        "browser: marks tests that require a real browser"
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests that are slow to run"
    )

    print(f"🔧 Pytest configured for AIReels project")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path: {sys.path[:3]}")

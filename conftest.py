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

# Fixtures globales
import pytest

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Asegurar que estamos usando variables de entorno de test
    os.environ.setdefault('INSTAGRAM_DRY_RUN', 'true')
    os.environ.setdefault('TEST_MODE', 'true')
    os.environ.setdefault('SKIP_BROWSER_LAUNCH', 'true')

    yield

    # Cleanup después de cada test
    pass

@pytest.fixture
def mock_browser_service():
    """Mock de BrowserService para tests."""
    from unittest.mock import AsyncMock, Mock
    mock_service = Mock()
    mock_service.page = AsyncMock()
    mock_service.wait_for_element = AsyncMock(return_value=True)
    mock_service.click_like_human = AsyncMock()
    mock_service.take_screenshot = AsyncMock()
    mock_service.get_element_text = AsyncMock(return_value="Test text")
    return mock_service

@pytest.fixture
def temp_video_file(tmp_path):
    """Crear archivo de video temporal para tests."""
    video_path = tmp_path / "test_video.mp4"
    video_path.write_bytes(b'dummy video content' * 100)
    return video_path

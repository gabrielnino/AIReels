"""
Helper functions for async testing.
"""
import asyncio
from unittest.mock import AsyncMock, Mock

def create_mock_browser_service():
    """Create a fully mocked BrowserService for testing."""
    mock_service = Mock()
    mock_service._is_initialized = True
    mock_service._page = AsyncMock()

    # Setup locator chain
    mock_locator = AsyncMock()
    mock_service._page.locator = Mock(return_value=mock_locator)

    return mock_service, mock_locator

def create_mock_element(is_visible=True, text=None):
    """Create a mocked element for testing."""
    mock_element = AsyncMock()

    if is_visible:
        mock_element.is_visible = AsyncMock(return_value=True)
    else:
        mock_element.is_visible = AsyncMock(side_effect=Exception("Not visible"))

    if text is not None:
        mock_element.text_content = AsyncMock(return_value=text)
    else:
        mock_element.text_content = AsyncMock(side_effect=Exception("Not found"))

    return mock_element

async def run_async_test(test_func):
    """Run async test function with proper event loop."""
    try:
        return await test_func()
    except Exception as e:
        print(f"Async test error: {e}")
        raise

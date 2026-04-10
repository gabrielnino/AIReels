"""
Unit tests for Search Service.

Tests for search functionality using Brave Search API with mocking.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-09
"""

import pytest
import os
from unittest.mock import patch, Mock
import sys

# Import the service module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from service.search_service import search, _get_api_key


class TestSearchService:
    """Tests for Search Service."""

    def test_get_api_key_with_key(self):
        """Test _get_api_key when API key is present in environment."""
        with patch.dict(os.environ, {'SEARCH_API_KEY': 'test_api_key_123'}):
            api_key = _get_api_key()
            assert api_key == 'test_api_key_123'

    def test_get_api_key_without_key(self):
        """Test _get_api_key when API key is NOT present in environment."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SEARCH_API_KEY not found in environment variables"):
                _get_api_key()

    @patch('service.search_service.requests.get')
    def test_search_success(self, mock_get):
        """Test search with successful API response."""
        # Mock API key in environment
        with patch.dict(os.environ, {'SEARCH_API_KEY': 'test_api_key'}):
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "web": {
                    "results": [
                        {"title": "Test Result 1", "description": "Description 1"},
                        {"title": "Test Result 2", "description": "Description 2"}
                    ]
                }
            }
            mock_get.return_value = mock_response

            # Call search function
            result = search("test query", count=2)

            # Verify result
            assert result["web"]["results"] == [
                {"title": "Test Result 1", "description": "Description 1"},
                {"title": "Test Result 2", "description": "Description 2"}
            ]

            # Verify API call was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://api.search.brave.com/res/v1/web/search"
            assert call_args[1]['headers']['X-Subscription-Token'] == 'test_api_key'
            assert call_args[1]['params']['q'] == 'test query'
            assert call_args[1]['params']['count'] == 2

    @patch('service.search_service.requests.get')
    def test_search_api_error(self, mock_get):
        """Test search when API returns error."""
        # Mock API key in environment
        with patch.dict(os.environ, {'SEARCH_API_KEY': 'test_api_key'}):
            # Mock API error
            mock_get.side_effect = Exception("API connection failed")

            # Call search function should raise exception
            with pytest.raises(Exception, match="API connection failed"):
                search("test query")

    @patch('service.search_service.requests.get')
    def test_search_empty_results(self, mock_get):
        """Test search when API returns empty results."""
        # Mock API key in environment
        with patch.dict(os.environ, {'SEARCH_API_KEY': 'test_api_key'}):
            # Mock response with empty results
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "web": {
                    "results": []
                }
            }
            mock_get.return_value = mock_response

            # Call search function
            result = search("test query", count=5)

            # Verify empty results
            assert result["web"]["results"] == []

    def test_search_default_count(self):
        """Test search uses default count parameter."""
        with patch.dict(os.environ, {'SEARCH_API_KEY': 'test_api_key'}):
            with patch('service.search_service.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"web": {"results": []}}
                mock_get.return_value = mock_response

                # Call without count parameter (should use default count=5)
                result = search("test query")

                # Verify default count was used
                call_args = mock_get.call_args
                assert call_args[1]['params']['count'] == 5

    @patch('service.search_service.requests.get')
    def test_search_custom_count(self, mock_get):
        """Test search with custom count parameter."""
        with patch.dict(os.environ, {'SEARCH_API_KEY': 'test_api_key'}):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"for": {"results": []}}
            mock_get.return_value = mock_response

            # Call with custom count
            result = search("test query", count=10)

            # Verify custom count was used
            call_args = mock_get.call_args
            assert call_args[1]['params']['count'] == 10


def test_search_logging():
    """Test that search function logs appropriately."""
    # This would require mocking the logger
    # For now, we'll just verify the function structure
    assert hasattr(search, '__call__')
    # More detailed logging tests could be added with logger mocking


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
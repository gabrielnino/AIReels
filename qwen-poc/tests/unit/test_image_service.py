"""
Unit tests for Image Service.

Tests for image generation functionality using Pollinations AI API with mocking.

Created by: Sam Lead Developer (Main Developer)
Date: 2026-04-09
"""

import pytest
import os
from unittest.mock import patch, Mock
import sys

# Import the service module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from service.image_service import (
    _build_pollinations_url,
    _generate_single_image,
    generate_image_urls,
    generate_images
)
from models.request_models import GenerateImageRequest


class TestImageService:
    """Tests for Image Service."""

    def test_build_pollinations_url(self):
        """Test building Pollinations AI URL."""
        # Test basic URL construction
        url = _build_pollinations_url("test prompt", width=1024, height=1024)

        # Should contain base URL
        assert "https://image.pollinations.ai/prompt" in url

        # Should contain encoded prompt
        assert "test" in url.lower()

        # Should contain width and height parameters
        assert "width=1024" in url
        assert "height=1024" in url

        # Should contain model parameter
        assert "model=flux" in url

        # Should contain seed parameter
        assert "seed=" in url

    def test_build_pollinations_url_custom_dimensions(self):
        """Test building Pollinations AI URL with custom dimensions."""
        url = _build_pollinations_url("custom prompt", width=512, height=768)

        assert "width=512" in url
        assert "height=768" in url

    @patch('service.image_service.requests.get')
    def test_generate_single_image_success(self, mock_get):
        """Test generating single image with successful API response."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake image content"
        mock_get.return_value = mock_response

        # Call function
        image_url = _generate_single_image("test prompt")

        # Should return a URL
        assert image_url.startswith("https://image.pollinations.ai/prompt")

        # Verify API call was made
        mock_get.assert_called_once()

    @patch('service.image_service.requests.get')
    def test_generate_single_image_empty_content(self, mock_get):
        """Test generating single image when API returns empty content."""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b""  # Empty content
        mock_get.return_value = mock_response

        # Call should raise RuntimeError
        with pytest.raises(RuntimeError, match="Pollinations returned empty content"):
            _generate_single_image("test prompt")

    @patch('service.image_service.requests.get')
    def test_generate_single_image_api_error(self, mock_get):
        """Test generating single image when API returns error."""
        # Mock API error
        mock_get.side_effect = Exception("API connection failed")

        # Call should raise exception
        with pytest.raises(Exception, match="API connection failed"):
            _generate_single_image("test prompt")

    @patch('service.image_service._generate_single_image')
    def test_generate_image_urls_single_prompt(self, mock_generate):
        """Test generating image URLs for single prompt."""
        # Mock image generation
        mock_generate.return_value = "https://image.pollinations.ai/prompt/test"

        request = GenerateImageRequest(
            prompts=["test prompt"],
            width=1024,
            height=1024,
            count=1
        )

        # Call function
        urls = generate_image_urls(request)

        # Should return list of URLs
        assert len(urls) == 1
        assert urls[0] == "https://image.pollinations.ai/prompt/test"

        # Verify generation was called
        mock_generate.assert_called_once_with("test prompt", 1024, 1024)

    @patch('service.image_service._generate_single_image')
    def test_generate_image_urls_multiple_prompts(self, mock_generate):
        """Test generating image URLs for multiple prompts."""
        # Mock image generation
        mock_generate.side_effect = [
            "https://image.pollinations.ai/prompt/test1",
            "https://image.pollinations.ai/prompt/test2",
            "https://image.pollinations.ai/prompt/test3"
        ]

        request = GenerateImageRequest(
            prompts=["test1", "test2", "test3"],
            width=1024,
            height=1024,
            count=3
        )

        # Call function
        urls = generate_image_urls(request)

        # Should return 3 URLs
        assert len(urls) == 3
        assert urls[0] == "https://image.pollinations.ai/prompt/test1"
        assert urls[1] == "https://image.pollinations.ai/prompt/test2"
        assert urls[2] == "https://image.pollinations.ai/prompt/test3"

        # Verify generation was called 3 times
        assert mock_generate.call_count == 3

    @patch('service.image_service._generate_single_image')
    @patch('service.image_service.download_image')
    def test_generate_images_success(self, mock_download, mock_generate):
        """Test generating images and downloading them."""
        # Mock image generation and download
        mock_generate.return_value = "https://image.pollinations.ai/prompt/test"
        mock_download.return_value = "/tmp/test_image.jpg"

        request = GenerateImageRequest(
            prompts=["test prompt"],
            width=1024,
            height=1024,
            count=1
        )

        # Call function
        paths = generate_images(request)

        # Should return list of file paths
        assert len(paths) == 1
        assert paths[0] == "/tmp/test_image.jpg"

        # Verify functions were called
        mock_generate.assert_called_once_with("test prompt", 1024, 1024)
        mock_download.assert_called_once()

    @patch('service.image_service._generate_single_image')
    def test_generate_images_different_dimensions(self, mock_generate):
        """Test generating images with different dimensions."""
        mock_generate.return_value = "https://image.pollinations.ai/prompt/test"

        request = GenerateImageRequest(
            prompts=["test prompt"],
            width=512,
            height=768,
            count=1
        )

        # We'll need to mock download_image too, but for now just verify generate call
        with patch('service.image_service.download_image'):
            generate_images(request)

        # Verify generation with custom dimensions
        mock_generate.assert_called_once_with("test prompt", 512, 768)

    def test_generate_image_urls_empty_prompts(self):
        """Test generating image URLs with empty prompts list."""
        request = GenerateImageRequest(
            prompts=[],
            width=1024,
            height=1024,
            count=0
        )

        # Should return empty list
        urls = generate_image_urls(request)
        assert urls == []

    @patch('service.image_service._generate_single_image')
    def test_generate_image_urls_count_less_than_prompts(self, mock_generate):
        """Test when count is less than number of prompts."""
        mock_generate.return_value = "https://image.pollinations.ai/prompt/test"

        request = GenerateImageRequest(
            prompts=["prompt1", "prompt2", "prompt3"],
            width=1024,
            height=1024,
            count=2  # Only generate 2 images from 3 prompts
        )

        urls = generate_image_urls(request)

        # Should generate only 2 images (first 2 prompts)
        assert len(urls) == 2
        assert mock_generate.call_count == 2

    @patch('service.image_service.requests.get')
    def test_generate_single_image_timeout(self, mock_get):
        """Test generating single image with timeout."""
        # Mock timeout error
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        # Call should raise timeout exception
        with pytest.raises(requests.exceptions.Timeout, match="Request timed out"):
            _generate_single_image("test prompt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
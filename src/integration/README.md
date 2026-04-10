# Integration Module

## Overview

The Integration Module provides a bridge between the content generation pipeline (qwen-poc) and the Instagram upload system. It handles data transformation, validation, and orchestration of the complete content creation workflow.

### Key Features:
- **Data Adapter**: Transforms qwen-poc output into standardized Instagram metadata
- **Mock Uploader**: Complete mocking system for testing without real Instagram access
- **Pipeline Bridge**: Orchestrates the complete workflow from generation to upload
- **Error Handling**: Robust error recovery and retry mechanisms
- **Performance Metrics**: Tracking of upload durations and success rates

## Architecture

The module follows a bridge pattern design, allowing different upload implementations (Graph API or Playwright UI) to work with the same interface.

### Main Components:
1. **Data Models** (`data_models.py`): Common data structures (VideoMetadata, UploadResult, UploadOptions)
2. **Metadata Adapter** (`metadata_adapter.py`): Transforms qwen-poc output to Instagram format
3. **Mock Uploader** (`mock_uploader.py`): Complete mocking system for testing
4. **Pipeline Bridge** (`pipeline_bridge.py`): Orchestration layer

## Installation

```bash
# Install dependencies
pip install pydantic pytest pytest-asyncio

# The module is part of the main AIReels project
# No separate installation required
```

## Quick Start

### Basic Usage Example:

```python
from src.integration.metadata_adapter import adapt_qwen_to_upload
from src.integration.pipeline_bridge import PipelineBridge
from src.integration.mock_uploader import MockInstagramUploader

# Example qwen-poc output
qwen_output = {
    "final_video_path": "/path/to/video.mp4",
    "caption": "Amazing AI-generated content",
    "topic": "AI Technology",
    "hashtags": ["AI", "Technology", "Future"]
}

# Convert to standardized metadata
metadata = adapt_qwen_to_upload(qwen_output)

# Create uploader (mock for testing)
uploader = MockInstagramUploader()

# Create pipeline bridge
bridge = PipelineBridge(uploader)

# Run complete pipeline
result = bridge.run_pipeline(qwen_output)

print(f"Upload result: {result.status}")
print(f"Media ID: {result.media_id}")
print(f"Duration: {result.total_duration_seconds} seconds")
```

## API Reference

### Data Models

#### `VideoMetadata`
```python
from src.integration.data_models import VideoMetadata

metadata = VideoMetadata(
    video_path="/path/to/video.mp4",
    caption="Your video caption",
    hashtags=["tag1", "tag2"],
    location="Optional location",
    schedule_time=None,  # Optional scheduling
    topic="Content topic",
    emotion="Emotional tone",
    cta="Call to action"
)
```

#### `UploadResult`
```python
from src.integration.data_models import UploadResult, UploadStatus

result = UploadResult(
    status=UploadStatus.COMPLETED,
    upload_id="unique-id",
    media_id="instagram-media-id",
    publish_time=datetime.now(),
    upload_duration_seconds=30.5,
    total_duration_seconds=45.2
)
```

### Metadata Adapter

#### `adapt_qwen_to_upload`
```python
from src.integration.metadata_adapter import adapt_qwen_to_upload

# Transform qwen-poc output
metadata = adapt_qwen_to_upload(qwen_output, options=None)

# With validation options
options = UploadOptions(
    max_retries=3,
    validate_before_upload=True,
    mock_mode=False
)
metadata = adapt_qwen_to_upload(qwen_output, options)
```

### Mock Uploader

#### `MockInstagramUploader`
```python
from src.integration.mock_uploader import MockInstagramUploader

# Create mock uploader with different behaviors
uploader = MockInstagramUploader()

# Always successful uploader
uploader = MockInstagramUploader(success_rate=1.0)

# Always failing uploader (for error testing)
uploader = MockInstagramUploader(success_rate=0.0)

# Flaky uploader (50% success)
uploader = MockInstagramUploader(success_rate=0.5)
```

### Pipeline Bridge

#### `PipelineBridge`
```python
from src.integration.pipeline_bridge import PipelineBridge

# Create bridge with any uploader implementation
bridge = PipelineBridge(uploader)

# Run complete pipeline
result = bridge.run_pipeline(qwen_output)

# With custom options
options = UploadOptions(max_retries=3, timeout_seconds=300)
result = bridge.run_pipeline(qwen_output, options)
```

## Examples

See the `examples/` directory for complete working examples:

### `integration_example.py`
Complete example showing the full pipeline from qwen-poc output to upload result, including error handling and performance metrics.

### `quick_demo.py`
Simplified demonstration of the metadata adapter and mock uploader for quick testing.

## Testing

The module includes comprehensive testing with pytest:

```bash
# Run all integration tests
python3 -m pytest tests/test_integration_pytest.py -v

# Run with coverage reporting
python3 -m pytest tests/test_integration_pytest.py --cov=src/integration --cov-report=term-missing
```

### Test Coverage:
- **data_models.py**: 80% coverage
- **metadata_adapter.py**: 58% coverage  
- **mock_uploader.py**: 56% coverage
- **pipeline_bridge.py**: 59% coverage
- **Total**: 63% coverage (10 tests, all passing)

## Error Handling

The module implements robust error handling with:

1. **Validation Errors**: Invalid metadata format, missing required fields
2. **Upload Errors**: Network failures, Instagram API errors, timeout
3. **Retry Mechanism**: Configurable retry logic with exponential backoff
4. **Fallback Strategies**: Mock mode fallback when real upload fails

## Configuration

### Environment Variables:
```bash
# Instagram upload configuration (optional for mock mode)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Upload options
INSTAGRAM_MAX_RETRIES=3
INSTAGRAM_TIMEOUT_SECONDS=300
INSTAGRAM_VALIDATE_BEFORE_UPLOAD=true
```

### UploadOptions:
```python
from src.integration.data_models import UploadOptions

options = UploadOptions(
    max_retries=3,
    timeout_seconds=300,
    validate_before_upload=True,
    mock_mode=False,  # Use real uploader
    success_rate_threshold=0.8  # Minimum success rate for batch operations
)
```

## Contributing

### Development Guidelines:
1. All changes must include unit tests
2. Maintain 80%+ test coverage for new code
3. Follow the bridge pattern for new upload implementations
4. Update examples when adding new features

### Code Style:
- Use Python 3.12+ type hints
- Follow Google Python style guide
- Include comprehensive docstrings
- Use async/await for async operations

## Performance Metrics

The module tracks various performance metrics:

1. **Upload Duration**: Time from start to completion
2. **Processing Duration**: Metadata adaptation and validation time
3. **Success Rate**: Percentage of successful uploads
4. **Retry Count**: Number of retries before success/failure

These metrics are available in the `UploadResult` object and can be used for monitoring and optimization.

## Next Steps

### Planned Improvements:
1. **Real Upload Implementations**: Graph API and Playwright UI uploaders
2. **Batch Processing**: Support for multiple videos in batch
3. **Advanced Scheduling**: Time-based and event-based scheduling
4. **Analytics Integration**: Integration with content performance analytics
5. **CI/CD Integration**: Automated testing and deployment pipelines

---

**Maintained by:** Jordan Documentation Specialist  
**Last Updated:** 2026-04-09  
**Version:** 1.0.0
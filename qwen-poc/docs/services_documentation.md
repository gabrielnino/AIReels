# AIReels Services Documentation

This document provides details on the core service modules used in the Qwen Proof of Concept (POC) pipeline: `image_service.py` and `video_service.py`. Both services interact with the Alibaba DashScope international API endpoints.

---

## 1. Image Service (`service/image_service.py`)

The Image Service is responsible for generating images using DashScope's multimodal conversational models (specifically the `qwen-image-2.0-pro` model). It can handle multimodal inputs consisting of multiple reference images and a text prompt.

### Key Dependencies
- `dashscope`: DashScope Python SDK for multimodal generation (`MultiModalConversation`).
- Uses `DASHSCOPE_API_KEY` from the environment.
- Configured to use the international endpoint: `https://dashscope-intl.aliyuncs.com/api/v1`

### Core Functions

#### `generate_image_urls(request_data: GenerateImageRequest) -> List[str]`
- **Description**: Submits an image generation request and returns the raw CDN URLs of the generated images. It skips the local download step, which makes it highly efficient for chaining directly into the video generation service.
- **Inputs**: A `GenerateImageRequest` containing `prompt` (text), `images` (list of URLs or local paths), `n` (number of generations), `negative_prompt`, and `seed`.
- **Outputs**: A list of string URLs (hosted on Alibaba CDN).

#### `generate_images(request_data: GenerateImageRequest) -> List[str]`
- **Description**: Submits an image generation request, retrieves the CDN URLs, and automatically downloads the generated images to the local `outputs/` directory.
- **Inputs**: Same as above (`GenerateImageRequest`).
- **Outputs**: A list of local file paths indicating where the generated images were saved.

### Internal Helper Functions
- `_build_messages`: Formats the `request_data` into the required `messages` payload for the DashScope API, converting local image paths to proper URI data strings (`to_file_uri`).
- `_call_api`: Invokes the synchronous API using the `dashscope` SDK.
- `_extract_image_urls`: Parses the sometimes inconsistently nested API response object (`message.content` or `choices[0].message.content`) to reliably pull out image URLs.

---

## 2. Video Service (`service/video_service.py`)

The Video Service handles asynchronous image-to-video (I2V) translation tasks using the `wan2.6-i2v` model via DashScope's REST API. Since video generation takes time, it implements an async submission and polling pipeline.

### Key Dependencies
- `requests`: Uses direct REST API calls rather than the Python SDK to interact with the async video synthesis endpoint.
- Uses `DASHSCOPE_API_KEY` from the environment.
- Target endpoint: `https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`

### Core Functions

#### `submit_video_task(img_url: str, prompt: str, ...) -> str`
- **Description**: Submits an asynchronous image-to-video task to DashScope.
- **Inputs**: 
  - `img_url`: The URL of the initial frame (e.g., a CDN URL returned by `generate_image_urls`).
  - `prompt`: The text description of the desired motion/video.
  - Parameters: `resolution` (default `720P`), `duration` (default 5 seconds), `audio` (whether to generate sound), `prompt_extend`, `shot_type`.
- **Outputs**: Returns a `task_id` (string) which is used to track the generation progress.

#### `poll_video_task(task_id: str, timeout: int = 600, interval: int = 10) -> str`
- **Description**: Continuously polls the status of a submitted video task until it either succeeds or fails. 
- **Behavior**: Sleeps for `interval` seconds between checks. Raises a `RuntimeError` if the task fails or a `TimeoutError` if it takes longer than the allowed `timeout`.
- **Outputs**: Returns the resulting `video_url` once the task status becomes `"SUCCEEDED"`.

#### `download_video(video_url: str) -> str`
- **Description**: Downloads the resulting video from the provided URL and saves it securely with a unique UUID to the `outputs/` directory.
- **Outputs**: Returns the local file path (e.g., `outputs/1234-abcd.mp4`).

#### `generate_video(img_url: str, prompt: str, ...) -> str`
- **Description**: A convenience wrapper that executes the complete synchronous pipeline: `submit -> poll -> download`.
- **Inputs**: The starting image URL, text prompt, resolution, duration, and audio flag.
- **Outputs**: Returns the final local file path to the generated `.mp4` video.

---

## 3. Workflow Pipeline Integration

The architecture of these two modules natively supports an end-to-end processing pipeline:
1. **Multimodal Input**: The user supplies text + images.
2. **Intermediate CDN Step**: Run `image_service.generate_image_urls()` to call `qwen-image-2.0-pro` and receive a temporary CDN URL.
3. **Video Synthesis**: Pass that CDN URL immediately into `video_service.generate_video()` alongside an animation prompt to submit to `wan2.6-i2v`.
4. **Local Artifact Registration**: The video service polls for completion and downloads the final `.mp4` into the `outputs/` folder.

import os
import dashscope
import logging
from dashscope import MultiModalConversation
from utils.file_utils import to_file_uri, download_image
from models.request_models import GenerateImageRequest
from typing import List, Tuple

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Use the international DashScope endpoint
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'


def _is_url(path: str) -> bool:
    """Returns True if the path is an HTTP/HTTPS URL."""
    return path.startswith("http://") or path.startswith("https://")


def _build_messages(request_data: GenerateImageRequest) -> list:
    """Builds the messages payload for the DashScope multimodal API."""
    messages_content = []
    for img in request_data.images:
        if _is_url(img):
            messages_content.append({"image": img})
        else:
            messages_content.append({"image": to_file_uri(img)})
    messages_content.append({"text": request_data.prompt})
    return [{"role": "user", "content": messages_content}]


def _call_api(request_data: GenerateImageRequest):
    """Calls the DashScope multimodal API and returns the raw response."""
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not found in environment variables.")
    return MultiModalConversation.call(
        api_key=api_key,
        model='qwen-image-2.0-pro',
        messages=_build_messages(request_data),
        result_format='message',
        stream=False,
        n=request_data.n,
        negative_prompt=request_data.negative_prompt or "",
        watermark=True,
        **(({"seed": request_data.seed} if request_data.seed is not None else {})),
    )


def _extract_image_urls(response) -> List[str]:
    """Parses the API response and returns a list of CDN image URLs."""
    urls = []
    try:
        choice = response.output.choices[0]
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            for item in choice.message.content:
                if isinstance(item, dict) and 'image' in item:
                    urls.append(item['image'])
    except AttributeError:
        output_choices = response.output.get('choices', [])
        if output_choices:
            content = output_choices[0].get('message', {}).get('content', [])
            for item in content:
                if isinstance(item, dict) and 'image' in item:
                    urls.append(item['image'])
    return urls


def generate_image_urls(request_data: GenerateImageRequest) -> List[str]:
    """
    Generates images and returns their raw CDN URLs (without downloading).
    Useful for chaining directly into video generation.
    """
    logging.info(f"[image_service.generate_image_urls] input values - request_data: {request_data.model_dump() if hasattr(request_data, 'model_dump') else request_data}")
    response = _call_api(request_data)
    if response.status_code == 200:
        urls = _extract_image_urls(response)
        print(f"[image] Generated {len(urls)} image URL(s)")
        logging.info(f"[image_service.generate_image_urls] output values: {urls}")
        return urls
    else:
        raise RuntimeError(f"DashScope API Error {response.status_code}: {response.message}")


def generate_images(request_data: GenerateImageRequest) -> List[str]:
    """
    Generates images, downloads them to outputs/, and returns local file paths.
    Uses the international endpoint (dashscope-intl.aliyuncs.com).
    """
    logging.info(f"[image_service.generate_images] input values - request_data: {request_data.model_dump() if hasattr(request_data, 'model_dump') else request_data}")
    try:
        urls = generate_image_urls(request_data)
        output_paths = []
        for url in urls:
            local_file = download_image(url)
            if local_file:
                output_paths.append(local_file)
        logging.info(f"[image_service.generate_images] output values: {output_paths}")
        return output_paths
    except Exception as e:
        print(f"Exception during DashScope image generation: {e}")
        raise e

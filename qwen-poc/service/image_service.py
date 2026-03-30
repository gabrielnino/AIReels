import os
import dashscope
from dashscope import MultiModalConversation
from utils.file_utils import to_file_uri, download_image
from models.request_models import GenerateImageRequest
from typing import List

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Use the international DashScope endpoint
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'


def _is_url(path: str) -> bool:
    """Returns True if the path is an HTTP/HTTPS URL."""
    return path.startswith("http://") or path.startswith("https://")


def generate_images(request_data: GenerateImageRequest) -> List[str]:
    """
    Builds the request using DashScope and the model qwen-image-2.0-pro.
    Uses the international endpoint (dashscope-intl.aliyuncs.com).
    """
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not found in environment variables.")

    # Build message content — support both public URLs and local file paths
    messages_content = []

    for img in request_data.images:
        if _is_url(img):
            messages_content.append({"image": img})
        else:
            uri = to_file_uri(img)
            messages_content.append({"image": uri})

    # Add text prompt
    messages_content.append({"text": request_data.prompt})

    messages = [
        {
            "role": "user",
            "content": messages_content
        }
    ]

    try:
        response = MultiModalConversation.call(
            api_key=api_key,
            model='qwen-image-2.0-pro',
            messages=messages,
            result_format='message',
            stream=False,
            n=request_data.n,
            negative_prompt=request_data.negative_prompt or "",
            watermark=True,
            **(({"seed": request_data.seed} if request_data.seed is not None else {})),
        )

        # Parse the response to extract image URLs
        if response.status_code == 200:
            print(f"API Call Success: {response}")

            output_paths = []

            try:
                choice = response.output.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    for item in choice.message.content:
                        if isinstance(item, dict) and 'image' in item:
                            url = item['image']
                            local_file = download_image(url)
                            if local_file:
                                output_paths.append(local_file)
            except AttributeError as e:
                print(f"Parsing structure error, checking pure dict format: {e}")
                output_choices = response.output.get('choices', [])
                if output_choices:
                    content = output_choices[0].get('message', {}).get('content', [])
                    for item in content:
                        if isinstance(item, dict) and 'image' in item:
                            url = item['image']
                            local_file = download_image(url)
                            if local_file:
                                output_paths.append(local_file)

            return output_paths
        else:
            print(f"Failed API Call: Code: {response.status_code}, Msg: {response.message}")
            raise RuntimeError(f"DashScope API Error {response.status_code}: {response.message}")

    except Exception as e:
        print(f"Exception during DashScope call: {e}")
        raise e

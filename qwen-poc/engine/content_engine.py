from service.llm_service import generate_text
from service.video_service import generate_video
from models.request_models import GenerateImageRequest
from utils.logger import get_logger

log = get_logger(__name__)


def expand_to_prompt(topic: str) -> str:
    """Uses DeepSeek to convert the short topic into a rich, cinematic image prompt."""
    log.step("expand_to_prompt", "IN", topic=topic)

    system_prompt = "You are an elite creative director specializing in AI prompt engineering for visual models."
    instructions = f"""
    Turn the following underlying topic into an exquisite, dense, highly described text prompt for a state-of-the-art Image Generator.

    Topic: '{topic}'

    Requirements:
    - Describe the scene with vivid details (e.g. lighting, dynamic angles, energy, colors, mood).
    - Ensure it is suitable as the opening frame of an engaging Instagram Reel.
    - KEEP IT CONCISE BUT DESCRIPTIVE (under 50 words).
    - DO NOT include conversational filler like "Here is your prompt:", just return the raw prompt text string.
    """

    response = generate_text(prompt=instructions, model="deepseek-chat", system_prompt=system_prompt)
    clean_prompt = response.strip()
    log.step("expand_to_prompt", "OUT", topic=topic, image_prompt=clean_prompt)
    return clean_prompt


def run_content_engine(selected_topic: str, strategy: dict) -> dict:
    """Full pipeline: Topic + Strategy → Image Prompt → Image → Video Reel."""
    log.step("run_content_engine", "IN",
             topic=selected_topic,
             motion_prompt=strategy.get("motion_prompt"),
             emotion=strategy.get("emotion"))

    # 1. Prompt Expansion
    log.step("run_content_engine", "INFO", step="1/3 - Expanding topic into image prompt")
    enhanced_prompt = expand_to_prompt(selected_topic)

    # 2. Image Generation via fal.ai Flux Dev
    log.step("run_content_engine", "INFO", step="2/3 - Generating base image", prompt=enhanced_prompt)
    from service.image_service import generate_image_urls
    img_req = GenerateImageRequest(prompt=enhanced_prompt, images=[], n=1)
    image_urls = generate_image_urls(img_req)

    if not image_urls:
        log.step("run_content_engine", "ERR", step="2/3", error="Image generation returned no URLs")
        raise ValueError("Image generation failed to return a URL.")

    base_image_url = image_urls[0]
    log.step("run_content_engine", "INFO", step="2/3 - Image ready", image_url=base_image_url)

    # 3. Video Generation via fal.ai Wan 2.1 i2v
    motion_prompt = strategy.get("motion_prompt", "gentle dynamic motion, cinematic camera pan, lively movement")
    log.step("run_content_engine", "INFO", step="3/3 - Submitting video task", motion_prompt=motion_prompt)

    video_path = generate_video(
        img_url=base_image_url,
        prompt=motion_prompt,
        resolution="720P",
        duration=10,
        audio=False
    )

    result = {
        "topic": selected_topic,
        "base_prompt": enhanced_prompt,
        "image_url": base_image_url,
        "final_video_path": video_path,
        "narrative": strategy.get("narrative"),
        "hook": strategy.get("hook"),
        "emotion": strategy.get("emotion"),
        "caption": strategy.get("caption"),
        "hashtags": strategy.get("hashtags", []),
        "cta": strategy.get("cta"),
        "on_screen_text": strategy.get("on_screen_text"),
    }

    log.step("run_content_engine", "OUT",
             topic=selected_topic,
             image_url=base_image_url,
             video_path=video_path,
             caption_preview=str(strategy.get("caption", ""))[:80])
    return result

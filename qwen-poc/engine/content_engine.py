from service.llm_service import generate_text
from service.image_service import generate_images
from service.video_service import generate_video
from models.request_models import GenerateImageRequest

def expand_to_prompt(topic: str) -> str:
    """Uses Qwen to convert the short topic into a rich, cinematic image prompt."""
    print(f"[Content Engine] Expanding '{topic}' into a cinematic prompt...")
    
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
    return clean_prompt

def run_content_engine(selected_topic: str, strategy: dict) -> dict:
    """Pipeline from Topic + Strategy -> Expanded Prompt -> Initial Image -> Video Reel."""

    # 1. Prompt Expansion (informed by strategy narrative and hook)
    enhanced_prompt = expand_to_prompt(selected_topic)
    print(f"[Content Engine] Extracted Prompt: {enhanced_prompt}")

    # 2. Image Generation
    print("[Content Engine] Generating base image frame...")
    img_req = GenerateImageRequest(prompt=enhanced_prompt, images=[], n=1)

    from service.image_service import generate_image_urls

    image_urls = generate_image_urls(img_req)
    if not image_urls:
        raise ValueError("Image generation failed to return a URL.")

    base_image_url = image_urls[0]
    print(f"[Content Engine] Generated Base Image URL: {base_image_url}")

    # 3. Video Generation — uses strategy motion_prompt instead of generic hardcoded one
    motion_prompt = strategy.get("motion_prompt", "gentle dynamic motion, cinematic camera pan, lively movement")
    print(f"[Content Engine] Motion Prompt: {motion_prompt}")
    print("[Content Engine] Submitting Video Synthesis task...")

    video_path = generate_video(
        img_url=base_image_url,
        prompt=motion_prompt,
        resolution="720P",
        duration=10,
        audio=False
    )

    print(f"[Content Engine] FULLY COMPLETED REEL! Video saved to: {video_path}")

    return {
        "topic": selected_topic,
        "base_prompt": enhanced_prompt,
        "image_url": base_image_url,
        "final_video_path": video_path,
        # Pass through strategy outputs for publishing
        "narrative": strategy.get("narrative"),
        "hook": strategy.get("hook"),
        "emotion": strategy.get("emotion"),
        "caption": strategy.get("caption"),
        "hashtags": strategy.get("hashtags", []),
        "cta": strategy.get("cta"),
        "on_screen_text": strategy.get("on_screen_text"),
    }

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm_client() -> OpenAI:
    """
    Initializes and returns an OpenAI-compatible client for DeepSeek.
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def generate_text(prompt: str, model: str = "deepseek-chat", system_prompt: str = None) -> str:
    """
    Generates text using DeepSeek.
    Defaults to deepseek-chat. Use 'deepseek-reasoner' for complex reasoning tasks.

    Args:
        prompt: The user instruction to generate text for.
        model: The model ID to use ('deepseek-chat' or 'deepseek-reasoner').
        system_prompt: Optional background context/instructions for the system role.

    Returns:
        The generated text string.
    """
    logging.info(f"[llm_service.generate_text] input values - prompt: {prompt}, model: {model}, system_prompt: {system_prompt}")
    client = get_llm_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    print(f"[llm] Calling model '{model}' with prompt preview: '{prompt[:50]}...'")

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        result = completion.choices[0].message.content
        logging.info(f"[llm_service.generate_text] output values: {result}")
        return result
    except Exception as e:
        print(f"[llm] Error communicating with DeepSeek LLM: {e}")
        raise

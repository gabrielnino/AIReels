import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)


def get_llm_client() -> OpenAI:
    """Initializes and returns an OpenAI-compatible client for DeepSeek."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def generate_text(prompt: str, model: str = "deepseek-chat", system_prompt: str = None) -> str:
    """
    Generates text using DeepSeek.
    Models: 'deepseek-chat' (default) | 'deepseek-reasoner' (complex reasoning)
    """
    log.step("generate_text", "IN", model=model, system_prompt_len=len(system_prompt or ""), prompt_preview=prompt[:80])

    client = get_llm_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    log.step("generate_text", "INFO", message_count=len(messages), total_prompt_chars=len(prompt))

    try:
        completion = client.chat.completions.create(model=model, messages=messages)
        result = completion.choices[0].message.content
        log.step("generate_text", "OUT", model=model, response_chars=len(result), response_preview=result[:120])
        return result
    except Exception as e:
        log.step("generate_text", "ERR", model=model, error=str(e))
        raise

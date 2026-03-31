import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_deepseek_client() -> OpenAI:
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

def generate_deepseek_text(prompt: str, model: str = "deepseek-chat", system_prompt: str = None) -> str:
    """
    Generates text using the DeepSeek model.
    Defaults to deepseek-chat, but can be overridden (e.g. deepseek-reasoner).
    
    Args:
        prompt: The user instruction to generate text for.
        model: The model ID to use ('deepseek-chat' or 'deepseek-reasoner').
        system_prompt: Optional background context/instructions for the system role.
        
    Returns:
        The generated text string.
    """
    logging.info(f"[deepseek_service.generate_deepseek_text] input values - prompt: {prompt}, model: {model}, system_prompt: {system_prompt}")
    client = get_deepseek_client()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        
    messages.append({"role": "user", "content": prompt})

    print(f"[deepseek] Calling model '{model}' with prompt: '{prompt[:50]}...'")

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        result = completion.choices[0].message.content
        logging.info(f"[deepseek_service.generate_deepseek_text] output values: {result}")
        return result
    except Exception as e:
        print(f"[deepseek] Error communicating with DeepSeek API: {e}")
        raise

import re


def strip_json_fences(text: str) -> str:
    """Strips markdown code fences (```json ... ``` or ``` ... ```) from LLM responses."""
    text = text.strip()
    if text.startswith("```json"):
        text = text.split("```json", 1)[1]
    elif text.startswith("```"):
        text = text.split("```", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def strip_json_comments(text: str) -> str:
    """Removes // inline comments from a JSON string so it can be parsed."""
    return re.sub(r"//[^\n]*", "", text)


def clean_llm_json(text: str) -> str:
    """Strips markdown fences and inline comments from an LLM JSON response."""
    return strip_json_comments(strip_json_fences(text))

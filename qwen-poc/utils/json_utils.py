import re


def strip_json_fences(text: str) -> str:
    """Strips markdown code fences and surrounding text from LLM JSON responses.
    Returns only the first top-level JSON object found."""
    text = text.strip()

    # Find first ```json or ``` block
    fence_match = re.search(r"```(?:json)?\s*\n", text)
    if fence_match:
        content = text[fence_match.end():]
        end = content.find("```")
        if end != -1:
            content = content[:end]
    else:
        # No code fence — try to extract first JSON object from raw text
        content = text

    # Extract only the first top-level JSON object
    # Find the first '{' and match its closing '}' respecting nesting
    depth = 0
    start = None
    for i, ch in enumerate(content):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                return content[start:i+1].strip()

    return content.strip()


def strip_json_comments(text: str) -> str:
    """Removes // inline comments from a JSON string so it can be parsed."""
    return re.sub(r"//[^\n]*", "", text)


def clean_llm_json(text: str) -> str:
    """Strips markdown fences and inline comments from an LLM JSON response."""
    return strip_json_comments(strip_json_fences(text))

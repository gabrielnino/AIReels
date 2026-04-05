import re


def strip_json_fences(text: str) -> str:
    """Strips markdown code fences and surrounding text from LLM JSON responses.
    Returns the first top-level JSON object or array found."""
    text = text.strip()

    # Find first ```json or ``` block
    fence_match = re.search(r"```(?:json)?\s*\n", text)
    if fence_match:
        content = text[fence_match.end():]
        end = content.find("```")
        if end != -1:
            content = content[:end]
    else:
        content = text

    # Find the first JSON delimiter ({ or [) by scanning for whichever comes first
    first_obj = None  # (char_type, start, content)
    first_arr = None
    for i, ch in enumerate(content):
        if ch == '{':
            if first_obj is None:
                first_obj = i
            break
        elif ch == '[':
            if first_arr is None:
                first_arr = i
            break

    # Process whichever comes first (or the only one found)
    start = None
    if first_obj is not None and (first_arr is None or first_obj < first_arr):
        depth = 0
        for i, ch in enumerate(content[first_obj:], first_obj):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return content[first_obj:i+1].strip()
        return content[first_obj:].strip()
    elif first_arr is not None:
        depth = 0
        for i, ch in enumerate(content[first_arr:], first_arr):
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    return content[first_arr:i+1].strip()
        return content[first_arr:].strip()

    return content.strip()


def strip_json_comments(text: str) -> str:
    """Removes // inline comments from a JSON string so it can be parsed."""
    return re.sub(r"//[^\n]*", "", text)


def clean_llm_json(text: str) -> str:
    """Strips markdown fences and inline comments from an LLM JSON response."""
    return strip_json_comments(strip_json_fences(text))

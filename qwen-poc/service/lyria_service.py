"""
lyria_service.py
================
Generates music tracks using Google Lyria 3 via OpenRouter.

Lyria produces high-quality 48kHz stereo audio from text prompts.
The audio is delivered as base64-encoded MP3 via streaming API calls.

Flow:
  1. submit_lyria_task()  → opens streaming connection to OpenRouter
  2. stream_audio()       → consumes SSE stream, extracts base64 audio chunks
  3. download_lyria()     → decodes base64 → saves MP3 to run directory
  4. generate_lyria_music() → orchestrates all three steps
"""

import json
import base64
import os
import time
import requests
import uuid
from utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

log = get_logger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LYRIA_MODEL = "google/lyria-3-clip-preview"


def submit_lyria_task(prompt: str, max_tokens: int = 65536) -> tuple[str, str]:
    """
    Opens a streaming connection to OpenRouter Lyria and returns
    (caption_text, audio_base64_data).

    The caption is a text description of the generated track.
    The audio data is the full base64-encoded MP3 concatenated.
    """
    log.step("submit_lyria_task", "IN", prompt_preview=prompt[:80])

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aireels.com",
        "X-Title": "AIReels",
    }

    payload = {
        "model": LYRIA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": max_tokens,
    }

    caption = ""
    audio_chunks = []
    start = time.time()

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        stream=True,
        timeout=180,
    )
    response.raise_for_status()

    for line in response.iter_lines():
        line_str = line.decode("utf-8") if isinstance(line, bytes) else line
        if not line_str.startswith("data: "):
            continue

        data_str = line_str[6:]
        if data_str == "[DONE]":
            break

        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            continue

        choices = data.get("choices", [])
        if not choices:
            continue

        delta = choices[0].get("delta", {})

        # Extract caption text
        content_delta = delta.get("content", "")
        if content_delta:
            caption += content_delta

        # Extract audio data (base64 MP3)
        audio_info = delta.get("audio", {})
        if isinstance(audio_info, dict) and "data" in audio_info:
            audio_chunks.append(audio_info["data"])

    elapsed = time.time() - start

    if not audio_chunks:
        log.step("submit_lyria_task", "ERR",
                 error="No audio data in stream",
                 caption_preview=caption[:200])
        raise RuntimeError("Lyria returned no audio data in stream response")

    full_b64 = "".join(audio_chunks)
    log.step("submit_lyria_task", "OUT",
             caption_len=len(caption),
             base64_len=len(full_b64),
             audio_chunks=len(audio_chunks),
             elapsed_s=round(elapsed, 1))

    return caption, full_b64


def download_lyria(base64_data: str) -> str:
    """
    Decodes the base64 audio data and saves as MP3 to the run directory.
    Returns the local file path.
    """
    from utils.run_context import get_run_dir
    log.step("download_lyria", "IN", base64_len=len(base64_data))

    run_dir = get_run_dir()
    filename = os.path.join(run_dir, f"lyria_{uuid.uuid4()}.mp3")

    audio_bytes = base64.b64decode(base64_data)

    # Lyria returns MP3 with ID3 tags — verify and save
    if len(audio_bytes) < 10:
        raise RuntimeError("Decoded audio data is too small (corrupted?)")

    with open(filename, "wb") as f:
        f.write(audio_bytes)

    size_kb = round(os.path.getsize(filename) / 1024)
    log.step("download_lyria", "OUT", filename=filename, size_kb=size_kb)
    return filename


def generate_lyria_music(prompt: str, duration: int = 15) -> str:
    """
    Full flow: prompt -> Lyria streaming -> decode base64 -> save MP3.
    Returns the local MP3 file path.
    """
    log.step("generate_lyria_music", "IN",
             prompt_preview=prompt[:80],
             duration=duration)

    # Append duration context if not already in prompt
    if f"{duration}" not in prompt.lower():
        prompt = f"{prompt}, {duration} seconds"

    caption, base64_data = submit_lyria_task(prompt)
    log.step("generate_lyria_music", "INFO", caption_preview=caption[:150])

    local_path = download_lyria(base64_data)

    log.step("generate_lyria_music", "OUT", local_path=local_path)
    return local_path


def lyria_to_wav(mp3_path: str, wav_path: str) -> str:
    """
    Converts an MP3 file to WAV using FFmpeg.
    Needed for mix_voice_and_music which expects WAV input.
    """
    import subprocess

    _PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
    FFMPEG_BIN = os.path.join(_PROJECT_ROOT, "ffmpeg")

    log.step("lyria_to_wav", "IN", mp3=mp3_path, wav=wav_path)

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", mp3_path,
        "-acodec", "pcm_s16le",
        "-ar", "48000",
        "-ac", "2",
        wav_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log.step("lyria_to_wav", "ERR", stderr=result.stderr[-600:])
        raise RuntimeError(f"FFmpeg MP3->WAV conversion failed:\n{result.stderr[-600:]}")

    size_kb = round(os.path.getsize(wav_path) / 1024)
    log.step("lyria_to_wav", "OUT", wav_path=wav_path, size_kb=size_kb)
    return wav_path

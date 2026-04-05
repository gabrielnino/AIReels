"""
voiceover_service.py
====================
Generates a voiceover for a Reel using fal.ai Kokoro TTS.

Kokoro produces natural-sounding speech in seconds — perfect for
10-second social media narration.

Available voices (pass as `voice` arg):
  af_sarah    American female, warm & conversational  ← default English
  af_bella    American female, expressive & energetic
  am_adam     American male, authoritative
  am_michael  American male, friendly & upbeat
  bf_emma     British female, elegant
  bm_george   British male, deep & confident

For Spanish, Kokoro v2 multilingual model is used with `es` language parameter.
Supported languages: "en" (default), "es"

Flow:
  1. submit_tts_task()   → queues Kokoro job on fal.ai
  2. poll_tts_task()     → waits until COMPLETED, returns CDN audio URL
  3. download_voiceover() → saves .wav to the run directory
  4. generate_voiceover() → orchestrates all three steps
"""

import os
import time
import uuid
import requests
from utils.logger import get_logger
from service.fal_client import FAL_API_BASE, get_fal_headers

log = get_logger(__name__)

FAL_TTS_MODEL = "fal-ai/kokoro"
FAL_TTS_MODEL_MULTI = "fal-ai/kokoro/v2"  # multilingual model (en + es)

DEFAULT_VOICES = {
    "en": "af_sarah",  # American female — warm & conversational
    "es": "sf_speech",  # Spanish female — warm & natural (Kokoro v2)
}


def _get_voice(language: str = "en") -> str:
    return DEFAULT_VOICES.get(language, DEFAULT_VOICES["en"])


# ── 1. Submit ─────────────────────────────────────────────────────────────────

def submit_tts_task(text: str, voice: str = DEFAULT_VOICES["en"], language: str = "en") -> dict:
    """Queues a Kokoro TTS job on fal.ai and returns task metadata.

    Uses fal-ai/kokoro for English, fal-ai/kokoro/v2 for other languages.
    """
    log.step("submit_tts_task", "IN", voice=voice, language=language, text_preview=text[:80])

    model = FAL_TTS_MODEL_MULTI if language != "en" else FAL_TTS_MODEL

    payload = {
        "text": text,
        "voice": voice,
    }
    if language != "en":
        payload["language"] = language

    response = requests.post(
        f"{FAL_API_BASE}/{model}",
        headers=get_fal_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    request_id = data.get("request_id")
    if not request_id:
        log.step("submit_tts_task", "ERR", error="No request_id in response", response=data)
        raise RuntimeError(f"No request_id in Kokoro TTS response: {data}")

    task = {
        "request_id": request_id,
        "status_url": data.get("status_url"),
        "response_url": data.get("response_url"),
    }
    log.step("submit_tts_task", "OUT", request_id=request_id, status_url=task["status_url"], model=model)
    return task


# ── 2. Poll ───────────────────────────────────────────────────────────────────

def poll_tts_task(task: dict, timeout: int = 120, interval: int = 3) -> str:
    """Polls fal.ai queue until COMPLETED and returns the audio CDN URL."""
    request_id = task["request_id"]
    status_url = task["status_url"]
    response_url = task["response_url"]

    log.step("poll_tts_task", "IN", request_id=request_id)

    headers = get_fal_headers()
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(status_url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        log.step("poll_tts_task", "INFO", request_id=request_id, status=status, elapsed_s=elapsed)

        if status == "COMPLETED":
            result_resp = requests.get(response_url, headers=headers, timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            # Kokoro returns { "audio": { "url": "..." } }
            audio_url = (
                result_data.get("audio", {}).get("url")
                or result_data.get("audio_url")
            )
            if not audio_url:
                log.step("poll_tts_task", "ERR",
                         request_id=request_id,
                         error="COMPLETED but no audio URL found",
                         result_data=result_data)
                raise RuntimeError(f"Kokoro TTS completed but no audio URL: {result_data}")

            log.step("poll_tts_task", "OUT", request_id=request_id, audio_url=audio_url)
            return audio_url

        elif status in ("FAILED", "CANCELLED"):
            log.step("poll_tts_task", "ERR", request_id=request_id, status=status, error=data.get("error"))
            raise RuntimeError(f"Kokoro TTS task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)

    raise TimeoutError(f"TTS task timed out after {timeout}s. Request ID: {request_id}")


# ── 3. Download ───────────────────────────────────────────────────────────────

def download_voiceover(audio_url: str) -> str:
    """Downloads the voiceover WAV and saves it to the current run directory."""
    from utils.run_context import get_run_dir
    log.step("download_voiceover", "IN", audio_url=audio_url)

    run_dir = get_run_dir()
    ext = ".mp3" if ".mp3" in audio_url else ".wav"
    filename = os.path.join(run_dir, f"voiceover_{uuid.uuid4()}{ext}")

    r = requests.get(audio_url, stream=True, timeout=60)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = round(os.path.getsize(filename) / 1024)
    log.step("download_voiceover", "OUT", filename=filename, size_kb=size_kb)
    return filename


# ── 4. Orchestrator ───────────────────────────────────────────────────────────

def generate_voiceover(
    script: str,
    language: str = "en",
    voice: str = None,
    cta_text: str = "",
) -> str:
    """
    Full flow: script → Kokoro TTS → download WAV.
    Returns local path to the voiceover audio file.

    Args:
        script    : Main narration text.
        language  : Language code — "en" (default) or "es".
                    Auto-selects appropriate voice if `voice` not set.
        voice     : Override voice explicitly (bypasses language auto-select).
        cta_text  : Optional CTA appended to the end of the audio.
    """
    resolved_voice = voice or _get_voice(language)
    log.step(
        "generate_voiceover", "IN",
        language=language, voice=resolved_voice,
        script_preview=script[:80], cta=cta_text[:60] if cta_text else "",
    )

    full_script = f"{script} {cta_text}".strip() if cta_text else script

    task = submit_tts_task(full_script, voice=resolved_voice, language=language)
    audio_url = poll_tts_task(task)
    local_path = download_voiceover(audio_url)

    log.step("generate_voiceover", "OUT", local_path=local_path)
    return local_path

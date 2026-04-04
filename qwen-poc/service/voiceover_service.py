"""
voiceover_service.py
====================
Generates an English voiceover for a Reel using fal.ai Kokoro TTS.

Kokoro produces natural-sounding speech in seconds — perfect for
10-second social media narration.

Available voices (pass as `voice` arg):
  af_sarah    American female, warm & conversational  ← default
  af_bella    American female, expressive & energetic
  am_adam     American male, authoritative
  am_michael  American male, friendly & upbeat
  bf_emma     British female, elegant
  bm_george   British male, deep & confident

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
DEFAULT_VOICE = "af_sarah"   # warm American female — works well for lifestyle reels


# ── 1. Submit ─────────────────────────────────────────────────────────────────

def submit_tts_task(text: str, voice: str = DEFAULT_VOICE) -> dict:
    """Queues a Kokoro TTS job on fal.ai and returns task metadata."""
    log.step("submit_tts_task", "IN", voice=voice, text_preview=text[:80])

    payload = {
        "text": text,
        "voice": voice,
    }

    response = requests.post(
        f"{FAL_API_BASE}/{FAL_TTS_MODEL}",
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
    log.step("submit_tts_task", "OUT", request_id=request_id, status_url=task["status_url"])
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

def generate_voiceover(script: str, voice: str = DEFAULT_VOICE) -> str:
    """
    Full flow: script → Kokoro TTS → download WAV.
    Returns local path to the voiceover audio file.
    """
    log.step("generate_voiceover", "IN", voice=voice, script_preview=script[:80])

    task = submit_tts_task(script, voice=voice)
    audio_url = poll_tts_task(task)
    local_path = download_voiceover(audio_url)

    log.step("generate_voiceover", "OUT", local_path=local_path)
    return local_path

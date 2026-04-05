"""
voiceover_service.py
====================
Generates a voiceover for a Reel.

TTS providers (auto-detected by priority):
  1. Edge TTS    — free, no API key, best quality for ES/EN
                  pip install edge-tts
                  Voices: es-ES/ es-MX (es), en-US (en)
  2. Kokoro      — requires FAL_API_KEY (fallback if edge-tts missing)

Supported languages: "en" (default), "es"

Flow:
  1. generate_voiceover() → picks best provider & generates audio
  2. Saved as .wav to the run directory
"""

import os
import uuid
import asyncio
import tempfile
import requests
from utils.logger import get_logger
from utils.run_context import get_run_dir

log = get_logger(__name__)

# ── Edge TTS voices (free, Microsoft) ─────────────────────────────────────────
EDGE_VOICES = {
    "en": "en-US-JennyNeural",   # warm American female
    "es": "es-MX-DaliaNeural",   # clear Mexican female — great for LatAm
}

# ── Kokoro voices (fal.ai, requires FAL_API_KEY) ─────────────────────────────
FAL_TTS_MODEL = "fal-ai/kokoro"

KOKORO_VOICES = {
    "en": "af_sarah",
    "es": "af_sarah",
}


# ── Availability check ────────────────────────────────────────────────────────

def _edge_tts_available() -> bool:
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return False


def _fal_api_available() -> bool:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return bool(os.environ.get("FAL_API_KEY"))
    except Exception:
        return False


# ── Edge TTS ──────────────────────────────────────────────────────────────────

def _generate_edge_tts(text: str, language: str = "en") -> str:
    """Generate speech using Edge TTS (free, no API key). Returns local .wav path."""
    import edge_tts

    voice = EDGE_VOICES.get(language, EDGE_VOICES["en"])
    log.step("edge_tts", "IN", voice=voice, text_preview=text[:80])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        rate = "+10%"  # slightly faster for social media
        communication = edge_tts.Communicate(text, voice, rate=rate)

        run_dir = get_run_dir()
        filename = os.path.join(run_dir, f"voiceover_{uuid.uuid4()}.wav")

        loop.run_until_complete(communication.save(filename))
        size_kb = round(os.path.getsize(filename) / 1024)
        log.step("edge_tts", "OUT", filename=filename, size_kb=size_kb)
        return filename
    finally:
        loop.close()


# ── Kokoro (fal.ai) ───────────────────────────────────────────────────────────
from service.fal_client import FAL_API_BASE, get_fal_headers


def _submit_tts_task(text: str, voice: str, language: str = "en") -> dict:
    """Queues a Kokoro TTS job on fal.ai."""
    log.step("submit_tts_task", "IN", voice=voice, language=language, text_preview=text[:80])

    payload = {
        "text": text,
        "voice": voice,
    }
    if language != "en":
        payload["language"] = language

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

    return {
        "request_id": request_id,
        "status_url": data.get("status_url"),
        "response_url": data.get("response_url"),
    }


def _poll_tts_task(task: dict, timeout: int = 120, interval: int = 3) -> str:
    """Polls fal.ai queue until COMPLETED and returns the audio CDN URL."""
    import time
    headers = get_fal_headers()
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(task["status_url"], headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "UNKNOWN")
        elapsed = int(time.time() - start)
        log.step("poll_tts_task", "INFO", status=status, elapsed_s=elapsed)

        if status == "COMPLETED":
            result_resp = requests.get(task["response_url"], headers=headers, timeout=30)
            result_resp.raise_for_status()
            result_data = result_resp.json()
            audio_url = (
                result_data.get("audio", {}).get("url")
                or result_data.get("audio_url")
            )
            if not audio_url:
                raise RuntimeError(f"Kokoro TTS completed but no audio URL: {result_data}")
            log.step("poll_tts_task", "OUT", audio_url=audio_url)
            return audio_url
        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Kokoro TTS task {status}: {data.get('error', 'No details')}")

        time.sleep(interval)
    raise TimeoutError(f"TTS task timed out after {timeout}s.")


def _download_audio(audio_url: str) -> str:
    """Downloads audio from a URL and saves it as .wav to the run directory."""
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


def _generate_kokoro(script: str, language: str = "en", voice: str = None) -> str:
    """Generate speech using Kokoro on fal.ai."""
    resolved_voice = voice or KOKORO_VOICES.get(language, KOKORO_VOICES["en"])
    log.step("generate_voiceover", "IN", provider="kokoro", language=language, voice=resolved_voice)

    task = _submit_tts_task(script, voice=resolved_voice, language=language)
    audio_url = _poll_tts_task(task)
    return _download_audio(audio_url)


# ── Orchestrator ──────────────────────────────────────────────────────────────

def generate_voiceover(
    script: str,
    language: str = "en",
    voice: str = None,
    cta_text: str = "",
    provider: str = None,  # "edge" or "kokoro" — auto-detect if None
) -> str:
    """
    Full flow: script → TTS → .wav file.

    Provider priority:
      1. Edge TTS (if edge-tts is installed via pip)
      2. Kokoro on fal.ai (if FAL_API_KEY is set)

    Args:
        script    : Main narration text.
        language  : "en" (default) or "es".
        voice     : Override voice explicitly.
        cta_text  : Optional CTA appended at the end.
        provider  : Force "edge" or "kokoro", auto-detects if None.
    """
    full_script = f"{script} {cta_text}".strip() if cta_text else script

    log.step(
        "generate_voiceover", "IN",
        language=language, script_preview=full_script[:80],
        cta=cta_text[:60] if cta_text else "",
    )

    # Auto-detect provider
    if provider is None:
        if _edge_tts_available():
            provider = "edge"
        elif _fal_api_available():
            provider = "kokoro"
        else:
            raise RuntimeError(
                "No TTS provider available.\n"
                "Options:\n"
                "  1. Install Edge TTS (free): pip install edge-tts\n"
                "  2. Set FAL_API_KEY for Kokoro (fal.ai)"
            )

    log.step("generate_voiceover", "INFO", provider=provider)

    if provider == "edge":
        return _generate_edge_tts(full_script, language=language)
    elif provider == "kokoro":
        return _generate_kokoro(full_script, language=language, voice=voice)
    else:
        raise ValueError(f"Unknown provider: {provider}")

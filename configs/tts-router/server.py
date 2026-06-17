import os
import asyncio
import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tts-router")

app = FastAPI(title="AIOS TTS Router", version="4.2.0")


@app.on_event("shutdown")
async def shutdown():
    await close_http_client()

# ── Shared HTTP client (connection pooling) ──
_http_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        limits = httpx.Limits(max_keepalive_connections=10, keepalive_expiry=60)
        _http_client = httpx.AsyncClient(timeout=30.0, limits=limits)
    return _http_client


async def close_http_client():
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None


# ── Backend endpoints ──
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY must be set in environment")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "Ukfq9vQ0QNLZ4MGK0Uxc")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"

UPLIFTAI_API_KEY = os.environ.get("UPLIFTAI_API_KEY")
if not UPLIFTAI_API_KEY:
    raise RuntimeError("UPLIFTAI_API_KEY must be set in environment")
UPLIFTAI_VOICE_ID = os.environ.get("UPLIFTAI_VOICE_ID", "helpdesk-agent")

TARGET_SAMPLE_RATE = int(os.environ.get("TARGET_SAMPLE_RATE", "24000"))
CHUNK_SIZE = 8192


def ffmpeg_cmd(input_args: list[str], filter_args: list[str] | None = None) -> list[str]:
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        *input_args,
        "-i", "pipe:0",
    ]
    if filter_args:
        cmd.extend(["-af", *filter_args])
    cmd.extend([
        "-f", "s16le", "-acodec", "pcm_s16le",
        "-ac", "1", "-ar", str(TARGET_SAMPLE_RATE),
        "pipe:1",
    ])
    return cmd


async def convert_to_pcm(audio_data: bytes, fmt: str) -> bytes:
    return await convert_to_pcm_speed(audio_data, fmt, 1.0)


async def convert_to_pcm_speed(audio_data: bytes, fmt: str, speed: float) -> bytes:
    filter_args = None
    if speed != 1.0:
        clamped = max(0.5, min(2.0, speed))
        filter_args = [f"atempo={clamped}"]

    if fmt == "pcm_22050":
        cmd = ffmpeg_cmd(["-f", "s16le", "-ar", "22050", "-ac", "1"], filter_args)
    elif fmt == "mp3":
        cmd = ffmpeg_cmd([], filter_args)
    elif fmt == "wav":
        cmd = ffmpeg_cmd([], filter_args)
    else:
        return audio_data

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(audio_data)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {stderr.decode()}")
    return stdout


# ── Backend TTS calls (async) ──

async def call_with_retry(fn, text_for_log: str, max_retries: int = 3) -> bytes:
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return await fn()
        except httpx.HTTPStatusError as e:
            last_exc = e
            status = e.response.status_code
            if status < 500:
                raise  # Don't retry 4xx errors
            if attempt < max_retries:
                wait = 0.5 * (2 ** (attempt - 1))
                logger.warning(f"Uplift AI 5xx (attempt {attempt}/{max_retries}), retrying in {wait:.1f}s: {status}")
                await asyncio.sleep(wait)
    logger.error(f"Uplift AI failed after {max_retries} retries: {last_exc}")
    raise last_exc


async def call_upliftai(text: str, speed: float = 1.0) -> bytes:
    payload = {
        "voiceId": UPLIFTAI_VOICE_ID,
        "text": text,
        "outputFormat": "PCM_22050_16",
    }
    if speed != 1.0:
        payload["speed"] = speed
    headers = {"Authorization": f"Bearer {UPLIFTAI_API_KEY}", "Content-Type": "application/json"}

    async def _do_call():
        client = await get_http_client()
        resp = await client.post(
            "https://api.upliftai.org/v1/synthesis/text-to-speech",
            json=payload, headers=headers
        )
        resp.raise_for_status()
        data = resp.content
        logger.info(f"Uplift AI TTS: speed={speed} {len(text)} chars -> {len(data)} bytes PCM 22050Hz")
        return data

    return await call_with_retry(_do_call, text)


async def call_elevenlabs(text: str) -> bytes:
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    client = await get_http_client()
    resp = await client.post(ELEVENLABS_URL, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.content


async def call_google_tts(text: str) -> bytes:
    import urllib.parse
    q = urllib.parse.quote(text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=ur&client=tw-ob"
    logger.info(f"Google TTS: {len(text)} chars")
    client = await get_http_client()
    resp = await client.get(url)
    resp.raise_for_status()
    return resp.content


# ── Routing ──

BACKEND_FORMATS = {
    "upliftai": "pcm_22050",
    "elevenlabs": "mp3",
    "google_tts": "mp3",
}


def get_backend(voice: str) -> str:
    if voice in ("uplift", "upliftai", "helpdesk-agent"):
        return "upliftai"
    if voice in ("urdu", "google_tts", "google"):
        return "google_tts"
    return "elevenlabs"


# ── Models ──

class TTSRequest(BaseModel):
    model: str = "tts-1"
    input: str
    voice: str = "default"
    response_format: str = "pcm"
    speed: float = 1.0
    language: str | None = None


class LegacyTTSRequest(BaseModel):
    text: str
    language: str | None = None
    speaker_wav: str | None = None


# ── Endpoints ──

@app.post("/v1/audio/speech")
async def synthesize(req: TTSRequest):
    backend_name = get_backend(req.voice)
    logger.info(f"TTS backend={backend_name} voice={req.voice} ({len(req.input)} chars): {req.input[:60]}")
    try:
        if backend_name == "upliftai":
            audio_data = await call_upliftai(req.input, req.speed)
        else:
            audio_data = await {
                "elevenlabs": call_elevenlabs,
                "google_tts": call_google_tts,
            }[backend_name](req.input)

        fmt = BACKEND_FORMATS[backend_name]
        pcm_data = await convert_to_pcm_speed(audio_data, fmt, req.speed)

        def chunk_gen():
            for i in range(0, len(pcm_data), CHUNK_SIZE):
                yield pcm_data[i:i + CHUNK_SIZE]

        return StreamingResponse(
            chunk_gen(),
            media_type=f"audio/L16;rate={TARGET_SAMPLE_RATE};channels=1",
        )
    except Exception as e:
        logger.error(f"{backend_name} failed: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"{backend_name} failed: {e}")


@app.post("/v1/text-to-speech")
async def tts_legacy(req: LegacyTTSRequest):
    return await synthesize(TTSRequest(input=req.text, voice="default"))


@app.get("/health")
async def health():
    return {"status": "ok", "version": "4.2.0"}


@app.get("/")
async def root():
    return {"service": "aios-tts-router", "version": "4.2.0"}

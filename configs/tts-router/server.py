import os
import logging
import subprocess
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tts-router")

app = FastAPI(title="AIOS TTS Router", version="3.0.0")

# ── Backend endpoints ──
CHATTERBOX_URL = os.environ.get("CHATTERBOX_URL", "http://10.40.0.30:4123/v1")
XTTS_URDU_URL = os.environ.get("XTTS_URDU_URL", "http://10.40.0.32:8020")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY must be set in environment")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "Ukfq9vQ0QNLZ4MGK0Uxc")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"

TARGET_SAMPLE_RATE = int(os.environ.get("TARGET_SAMPLE_RATE", "24000"))


# ── Backend TTS calls ──

def call_elevenlabs(text: str) -> bytes:
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    resp = requests.post(ELEVENLABS_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.content


def call_chatterbox(text: str) -> bytes:
    payload = {
        "model": "tts-1",
        "input": text,
        "voice": "default",
        "response_format": "wav",
        "speed": 1.0,
    }
    resp = requests.post(f"{CHATTERBOX_URL}/audio/speech", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.content  # WAV bytes


def call_xtts_urdu(text: str) -> bytes:
    payload = {
        "text": text,
        "language": "ur",
        "temperature": 0.1,
        "top_p": 0.3,
        "top_k": 10,
    }
    resp = requests.post(f"{XTTS_URDU_URL}/v1/tts", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.content  # WAV bytes


def call_google_tts(text: str) -> bytes:
    import urllib.parse
    q = urllib.parse.quote(text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=ur&client=tw-ob"
    logger.info(f"Google TTS: {len(text)} chars")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content  # MP3 bytes


# ── Audio conversion ──

def audio_to_pcm(audio_bytes: bytes, ext: str) -> bytes:
    tmp_in = f"/tmp/tts_in_{os.getpid()}.{ext}"
    tmp_out = f"/tmp/tts_out_{os.getpid()}.raw"
    try:
        with open(tmp_in, "wb") as f:
            f.write(audio_bytes)
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", tmp_in,
            "-f", "s16le", "-acodec", "pcm_s16le",
            "-ac", "1", "-ar", str(TARGET_SAMPLE_RATE),
            tmp_out,
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, err = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {err.decode()}")
        with open(tmp_out, "rb") as f:
            pcm = f.read()
        secs = len(pcm) / 2 / TARGET_SAMPLE_RATE
        logger.info(f"Converted {ext}→PCM ({len(pcm)} B, {secs:.2f}s)")
        return pcm
    finally:
        for f in [tmp_in, tmp_out]:
            try:
                os.remove(f)
            except OSError:
                pass


# ── Routing ──

TTS_BACKENDS = {
    "chatterbox": {"call": call_chatterbox, "ext": "wav"},
    "xtts_urdu": {"call": call_xtts_urdu, "ext": "wav"},
    "google_tts": {"call": call_google_tts, "ext": "mp3"},
    "elevenlabs": {"call": call_elevenlabs, "ext": "mp3"},
}


def get_backend(voice: str) -> str:
    if voice in ("chatterbox", "hf_alpha"):
        return "chatterbox"
    if voice in ("xtts_urdu", "xtts"):
        return "xtts_urdu"
    if voice in ("urdu", "google_tts", "google"):
        return "google_tts"
    return "elevenlabs"


# ── Models ──

class TTSRequest(BaseModel):
    model: str = "tts-1"
    input: str
    voice: str = "default"
    response_format: str = "wav"
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
    backend = TTS_BACKENDS[backend_name]
    logger.info(f"TTS backend={backend_name} voice={req.voice} ({len(req.input)} chars): {req.input[:60]}")
    try:
        audio = backend["call"](req.input)
        pcm = audio_to_pcm(audio, backend["ext"])
        return Response(content=pcm, media_type=f"audio/L16;rate={TARGET_SAMPLE_RATE};channels=1")
    except Exception as e:
        logger.error(f"{backend_name} failed: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"{backend_name} failed: {e}")


@app.post("/v1/text-to-speech")
async def tts_legacy(req: LegacyTTSRequest):
    return await synthesize(TTSRequest(input=req.text, voice="default"))


@app.get("/health")
async def health():
    return {"status": "ok", "default_backend": "elevenlabs", "chatterbox_url": CHATTERBOX_URL}


@app.get("/")
async def root():
    return {"service": "aios-tts-router", "version": "3.0.0"}

import os
import json
import logging
import subprocess
import io
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tts-router")

app = FastAPI(title="AIOS TTS Router", version="2.0.0")

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY must be set in environment")
ELEVENLABS_VOICE_ID = os.environ.get(
    "ELEVENLABS_VOICE_ID",
    "Ukfq9vQ0QNLZ4MGK0Uxc"
)
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"

HEADERS = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}


TARGET_SAMPLE_RATE = int(os.environ.get("TARGET_SAMPLE_RATE", "24000"))


def call_elevenlabs(text: str) -> bytes:
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    resp = requests.post(ELEVENLABS_URL, json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.content


def mp3_to_pcm(mp3_bytes: bytes) -> bytes:
    logger.info(f"Converting MP3 ({len(mp3_bytes)} bytes) to {TARGET_SAMPLE_RATE}Hz raw PCM")
    # Write MP3 to temp file, then ffmpeg to raw PCM
    tmp_in = f"/tmp/tts_in_{os.getpid()}.mp3"
    tmp_out = f"/tmp/tts_out_{os.getpid()}.raw"
    try:
        with open(tmp_in, "wb") as f:
            f.write(mp3_bytes)
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", tmp_in,
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", str(TARGET_SAMPLE_RATE),
            tmp_out
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, err = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg conversion failed: {err.decode()}")
        with open(tmp_out, "rb") as f:
            pcm = f.read()
        logger.info(f"Converted to PCM ({len(pcm)} bytes, {len(pcm)/2/TARGET_SAMPLE_RATE:.2f}s)")
        return pcm
    finally:
        for f in [tmp_in, tmp_out]:
            try:
                os.remove(f)
            except OSError:
                pass


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


@app.post("/v1/audio/speech")
async def synthesize(req: TTSRequest):
    logger.info(f"ElevenLabs TTS ({len(req.input)} chars): {req.input[:60]}")
    try:
        mp3 = call_elevenlabs(req.input)
        pcm = mp3_to_pcm(mp3)
        return Response(content=pcm, media_type="audio/L16;rate=24000;channels=1")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs failed: {e}")


@app.post("/v1/text-to-speech")
async def tts_legacy(req: LegacyTTSRequest):
    logger.info(f"ElevenLabs TTS legacy ({len(req.text)} chars): {req.text[:60]}")
    try:
        mp3 = call_elevenlabs(req.text)
        pcm = mp3_to_pcm(mp3)
        return Response(content=pcm, media_type="audio/L16;rate=24000;channels=1")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs failed: {e}")


@app.get("/health")
async def health():
    return {"status": "ok", "backend": "ElevenLabs", "voice_id": ELEVENLABS_VOICE_ID}


@app.get("/")
async def root():
    return {"service": "aios-tts-router", "version": "2.0.0", "backend": "ElevenLabs"}

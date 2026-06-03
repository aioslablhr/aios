import os
import io
import json
import logging
import requests
import urllib.request
import urllib.parse
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tts-router")

app = FastAPI(title="AIOS TTS Router", version="1.0.0")

XTTS_URL = os.environ.get("XTTS_URL", "http://10.40.0.32:8020/v1/tts")
CHATTERBOX_URL = os.environ.get("CHATTERBOX_URL", "http://10.40.0.30:4123/v1/audio/speech")
KOKORO_URL = os.environ.get("KOKORO_URL", "http://10.40.0.31:8880/v1/audio/speech")

# Simple character-range-based Urdu detection
URDU_RANGE = range(0x0600, 0x06FF + 1)
ARABIC_RANGE = range(0x0750, 0x077F + 1)


def has_urdu(text: str) -> bool:
    for ch in text:
        cp = ord(ch)
        if cp in URDU_RANGE or cp in ARABIC_RANGE:
            return True
    return False


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
    text = req.input
    lang = req.language or ""

    if not lang:
        lang = "ur" if has_urdu(text) else "en"

    if lang.startswith("ur"):
        logger.info(f"Routing to XTTS (Urdu): {text[:60]}")
        try:
            payload = {"text": text, "language": "ur"}
            resp = requests.post(XTTS_URL, json=payload, timeout=60)
            resp.raise_for_status()
            return Response(content=resp.content, media_type="audio/wav")
        except Exception as e:
            logger.warning(f"XTTS failed ({e}), falling back to Chatterbox")
            lang = "en"

    if lang.startswith("en") or lang.startswith("ar"):
        logger.info(f"Routing to Chatterbox (English): {text[:60]}")
        try:
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": req.voice,
                "response_format": req.response_format,
                "speed": req.speed,
            }
            resp = requests.post(CHATTERBOX_URL, json=payload, timeout=60)
            resp.raise_for_status()
            return Response(content=resp.content, media_type=f"audio/{req.response_format}")
        except Exception as e:
            logger.warning(f"Chatterbox failed ({e}), falling back to Kokoro")

    logger.info(f"Routing to Kokoro (CPU fallback): {text[:60]}")
    try:
        payload = {"model": "tts-1", "input": text, "voice": req.voice}
        resp = requests.post(KOKORO_URL, json=payload, timeout=60)
        resp.raise_for_status()
        return Response(content=resp.content, media_type=f"audio/{req.response_format}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"All TTS backends failed: {e}")


@app.post("/v1/text-to-speech")
async def tts_legacy(req: LegacyTTSRequest):
    text = req.text
    lang = req.language or ("ur" if has_urdu(text) else "en")

    if lang.startswith("ur"):
        try:
            payload = {"text": text, "language": "ur"}
            resp = requests.post(XTTS_URL, json=payload, timeout=60)
            resp.raise_for_status()
            return Response(content=resp.content, media_type="audio/wav")
        except:
            lang = "en"

    try:
        payload = {"model": "tts-1", "input": text, "voice": "default"}
        resp = requests.post(CHATTERBOX_URL, json=payload, timeout=60)
        resp.raise_for_status()
        return Response(content=resp.content, media_type=f"audio/wav")
    except:
        pass

    try:
        payload = {"model": "tts-1", "input": text, "voice": "default"}
        resp = requests.post(KOKORO_URL, json=payload, timeout=60)
        resp.raise_for_status()
        return Response(content=resp.content, media_type=f"audio/wav")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS failed: {e}")


@app.get("/health")
async def health():
    backends = {}
    for name, url in [("xtts", XTTS_URL), ("chatterbox", CHATTERBOX_URL), ("kokoro", KOKORO_URL)]:
        try:
            r = requests.get(url.replace("/v1/audio/speech", "/health").replace("/v1/tts", "/health"), timeout=3)
            backends[name] = "ok" if r.status_code == 200 else f"http_{r.status_code}"
        except Exception as e:
            backends[name] = f"unreachable: {str(e)[:40]}"
    return {"status": "ok", "backends": backends}


@app.get("/")
async def root():
    return {"service": "aios-tts-router", "version": "1.0.0", "docs": "/docs"}

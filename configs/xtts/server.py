import os
import io
import json
import logging
import torch
import soundfile as sf
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xtts-urdu")

app = FastAPI(title="XTTS-v2-Urdu-FT", version="1.0.0")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_REPO = os.environ.get("XTTS_MODEL_REPO", "arbml/xtts-v2-urdu-ft")
MODEL_CACHE = Path("/app/model_cache")
model = None


def download_hf_file(repo_id: str, filename: str, dest: Path):
    import requests
    url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        logger.info(f"Downloading {url}")
        resp = requests.get(url, timeout=300)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            f.write(resp.content)
        logger.info(f"Saved to {dest}")


def load_model():
    global model
    try:
        from TTS.api import TTS
        model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=DEVICE == "cuda")

        speaker_path = MODEL_CACHE / "speaker.wav"
        if not speaker_path.exists():
            download_hf_file(MODEL_REPO, "speaker.wav", speaker_path)
        os.environ["XTTS_SPEAKER_WAV"] = str(speaker_path)
        logger.info(f"XTTS-v2-Urdu-FT ready on {DEVICE}")
    except Exception as e:
        logger.warning(f"XTTS-v2-Urdu-FT load failed: {e}")
        model = None


@app.on_event("startup")
async def startup():
    load_model()


class TTSRequest(BaseModel):
    text: str
    language: str = "ur"
    speaker_wav: str | None = None


@app.post("/v1/tts")
async def synthesize(req: TTSRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="XTTS model not loaded")
    try:
        speaker = req.speaker_wav or os.environ.get("XTTS_SPEAKER_WAV", "")
        wav = model.tts(text=req.text, language=req.language, speaker_wav=speaker)
        buffer = io.BytesIO()
        sf.write(buffer, wav, 24000, format="wav")
        buffer.seek(0)
        return Response(content=buffer.read(), media_type="audio/wav")
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok" if model else "deferred", "device": DEVICE}


@app.get("/")
async def root():
    return {"service": "xtts-v2-urdu-ft", "version": "1.0.0", "loaded": model is not None}

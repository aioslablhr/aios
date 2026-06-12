import os, io, logging, torch, soundfile as sf
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dia-urdu")

app = FastAPI(title="Dia-1.6B-Urdu TTS", version="1.0.0")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_CACHE = Path("/app/model_cache")
MODEL_CACHE.mkdir(parents=True, exist_ok=True)

model = None


def load_model():
    global model
    try:
        from dia.model import Dia

        logger.info("Loading base Dia-1.6B model...")
        model = Dia.from_pretrained("nari-labs/Dia-1.6B", device=DEVICE)

        logger.info("Downloading Urdu fine-tune weights...")
        ckpt_path = hf_hub_download(
            repo_id="mahwizzzz/Dia-1.6B-Urdu",
            filename="model.pth",
            cache_dir=str(MODEL_CACHE),
        )

        logger.info("Loading Urdu fine-tune weights...")
        ckpt = torch.load(ckpt_path, map_location=DEVICE)
        model.model.load_state_dict(ckpt, strict=True)
        model.model.eval()
        model.model = model.model.float()

        logger.info(f"Dia-1.6B-Urdu ready on {DEVICE}")
    except Exception as e:
        logger.error(f"Model load failed: {e}")
        import traceback
        traceback.print_exc()
        model = None


@app.on_event("startup")
async def startup():
    load_model()


class TTSRequest(BaseModel):
    model: str = "dia-1.6b-urdu"
    input: str
    voice: str = "default"
    response_format: str = "wav"
    speed: float = 1.0


@app.post("/v1/audio/speech")
async def synthesize(req: TTSRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Dia model not loaded")
    try:
        text = req.input
        if not text.startswith("[ur]"):
            text = f"[ur] {text}"

        with torch.no_grad():
            output = model.generate(
                text,
                max_tokens=512,
                cfg_scale=3.0,
            )

        buffer = io.BytesIO()
        sf.write(buffer, output, 44100, format="wav")
        buffer.seek(0)
        return Response(content=buffer.read(), media_type="audio/wav")
    except Exception as e:
        logger.error(f"Dia TTS failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/tts")
async def tts_legacy(text: str, language: str = "ur"):
    return await synthesize(TTSRequest(input=text))


@app.get("/health")
async def health():
    return {"status": "ok" if model else "deferred", "device": DEVICE}


@app.get("/")
async def root():
    return {
        "service": "dia-1.6b-urdu-tts",
        "version": "1.0.0",
        "loaded": model is not None,
        "device": DEVICE,
    }

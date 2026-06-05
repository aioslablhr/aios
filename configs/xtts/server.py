import os, io, logging, torch, soundfile as sf, requests, shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xtts-urdu")
app = FastAPI(title="XTTS-v2-Urdu-FT", version="1.0.0")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_REPO = os.environ.get("XTTS_MODEL_REPO", "suhaibrashid17/XTTS-v2-Urdu-FT")
MODEL_CACHE = Path("/app/model_cache")
MODEL_CACHE.mkdir(parents=True, exist_ok=True)
model = None

def download_hf_file(repo_id, filename, dest):
    url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    headers = {}
    token = os.environ.get("HF_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if not dest.exists():
        logger.info(f"Downloading {url}")
        resp = requests.get(url, headers=headers, timeout=600, stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Saved {dest} ({dest.stat().st_size / 1e9:.2f} GB)")

def fix_tokenizer_init(path):
    if not path.exists():
        return False
    code = path.read_text()
    old = "            self.tokenizer = Tokenizer.from_file(vocab_file)"
    new = """            with open(vocab_file, encoding="utf-8") as _f:
                _td = __import__("json").load(_f)
            _md = _td.get("model", {})
            _BPE = __import__("tokenizers.models", fromlist=["BPE"]).BPE
            _Tok = __import__("tokenizers", fromlist=["Tokenizer"]).Tokenizer
            self.tokenizer = _Tok(_BPE(
                vocab=_md.get("vocab", {}), merges=[tuple(m) for m in _md.get("merges", [])],
                unk_token="[UNK]",
            ))"""
    if old in code:
        code = code.replace(old, new)
        path.write_text(code)
        logger.info("Tokenizer __init__ fixed for tokenizers >=0.19")
        return True
    logger.warning("Could not find from_file line in tokenizer")
    return False

def patch_tokenizer():
    custom_path = MODEL_CACHE / "tokenizer.py"
    if not custom_path.exists():
        return
    fix_tokenizer_init(custom_path)
    import TTS.tts.layers.xtts.tokenizer as tok_mod
    orig_path = tok_mod.__file__
    shutil.copy2(str(custom_path), orig_path)
    import sys
    for name in list(sys.modules):
        if "xtts.tokenizer" in name:
            del sys.modules[name]
    logger.info("Tokenizer patched")

def load_model():
    global model
    try:
        for f in ["config.json", "model.pth", "vocab.json", "tokenizer.py"]:
            download_hf_file(MODEL_REPO, f, MODEL_CACHE / f)
        patch_tokenizer()
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import Xtts
        cfg = XttsConfig()
        cfg.load_json(str(MODEL_CACHE / "config.json"))
        model = Xtts.init_from_config(cfg)
        model.load_checkpoint(
            cfg,
            checkpoint_dir=str(MODEL_CACHE),
            checkpoint_path=str(MODEL_CACHE / "model.pth"),
            vocab_path=str(MODEL_CACHE / "vocab.json"),
            eval=True, strict=False, use_deepspeed=False,
        )
        model.to(DEVICE)
        model.eval()
        # Create default speaker latents from a short noise reference
        default_spk = MODEL_CACHE / "default_speaker.wav"
        if not default_spk.exists():
            import torchaudio
            dummy = torch.randn(1, 24000)
            torchaudio.save(str(default_spk), dummy, 24000)
        gpt_default, spk_default = model.get_conditioning_latents(
            audio_path=[str(default_spk)],
            gpt_cond_len=model.config.gpt_cond_len,
            max_ref_length=model.config.max_ref_len,
            sound_norm_refs=model.config.sound_norm_refs,
        )
        model.default_gpt_cond = gpt_default
        model.default_spk_emb = spk_default
        logger.info(f"XTTS-v2-Urdu-FT ready on {DEVICE}")
    except Exception as e:
        logger.warning(f"XTTS load failed: {e}")
        import traceback; traceback.print_exc()
        model = None

@app.on_event("startup")
async def startup():
    load_model()

class TTSRequest(BaseModel):
    text: str
    language: str = "ur"
    speaker_wav: str | None = None
    temperature: float = 0.1
    top_p: float = 0.3
    top_k: int = 10

@app.post("/v1/tts")
async def synthesize(req: TTSRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="XTTS model not loaded")
    try:
        if req.speaker_wav:
            spk_path = MODEL_CACHE / "speaker_custom.wav"
            resp = requests.get(req.speaker_wav, timeout=60)
            if resp.status_code == 200:
                with open(spk_path, "wb") as f:
                    f.write(resp.content)
                gpt_cond, spk_emb = model.get_conditioning_latents(
                    audio_path=[str(spk_path)],
                    gpt_cond_len=model.config.gpt_cond_len,
                    max_ref_length=model.config.max_ref_len,
                    sound_norm_refs=model.config.sound_norm_refs,
                )
            else:
                gpt_cond, spk_emb = model.default_gpt_cond, model.default_spk_emb
        else:
            gpt_cond, spk_emb = model.default_gpt_cond, model.default_spk_emb
        out = model.inference(
            text=req.text, language=req.language,
            gpt_cond_latent=gpt_cond, speaker_embedding=spk_emb,
            temperature=req.temperature, length_penalty=0.1,
            repetition_penalty=10.0, top_k=req.top_k, top_p=req.top_p,
        )
        buffer = io.BytesIO()
        sf.write(buffer, torch.tensor(out["wav"]), 24000, format="wav")
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

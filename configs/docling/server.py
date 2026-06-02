import os
import json
import tempfile
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docling")

try:
    from markitdown import MarkItDown
    md_parser = MarkItDown()
    PARSER_READY = True
    logger.info("MarkItDown parser initialized")
except ImportError:
    md_parser = None
    PARSER_READY = False
    logger.warning("MarkItDown not available")

try:
    import boto3
    from botocore.config import Config
    BOTO_READY = True
except ImportError:
    boto3 = None
    BOTO_READY = False

app = FastAPI(title="AIOS Document Parser", version="1.0.0")

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "10.30.0.40:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")


class MinioParseRequest(BaseModel):
    bucket: str
    key: str
    delete_after: bool = False


class ParseResult(BaseModel):
    filename: str
    content_type: str
    markdown: str
    metadata: dict
    characters: int
    chunks: list[str] | None = None


def chunk_text(text: str, max_chars: int = 2000, overlap: int = 200) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space > start + max_chars // 2:
                end = last_space
        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else end
    return [c for c in chunks if c]


@app.post("/v1/parse")
async def parse_upload(file: UploadFile = File(...), chunk: bool = Form(False)):
    if not PARSER_READY:
        return {"status": "error", "detail": "Parser not available"}

    content = await file.read()
    suffix = Path(file.filename or "upload").suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = md_parser.convert(tmp_path)
        text = result.text_content or ""
        meta = {"title": result.title or file.filename, "format": suffix}

        return {
            "status": "ok",
            "result": ParseResult(
                filename=file.filename or "unknown",
                content_type=suffix,
                markdown=text,
                metadata=meta,
                characters=len(text),
                chunks=chunk_text(text) if chunk else None,
            ).model_dump(),
        }
    except Exception as e:
        logger.error(f"Parse failed: {e}")
        return {"status": "error", "detail": str(e)}
    finally:
        os.unlink(tmp_path)


@app.post("/v1/parse/minio")
def parse_from_minio(req: MinioParseRequest):
    if not PARSER_READY:
        return {"status": "error", "detail": "Parser not available"}
    if not BOTO_READY:
        return {"status": "error", "detail": "boto3 not available"}

    s3 = boto3.client(
        "s3",
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        try:
            s3.download_file(req.bucket, req.key, tmp.name)
        except Exception as e:
            os.unlink(tmp.name)
            return {"status": "error", "detail": f"MinIO download failed: {e}"}

    suffix = Path(req.key).suffix.lower()
    try:
        result = md_parser.convert(tmp.name)
        text = result.text_content or ""

        if req.delete_after:
            try:
                s3.delete_object(Bucket=req.bucket, Key=req.key)
            except Exception:
                pass

        return {
            "status": "ok",
            "result": ParseResult(
                filename=req.key,
                content_type=suffix,
                markdown=text,
                metadata={"title": result.title or req.key, "bucket": req.bucket, "key": req.key},
                characters=len(text),
                chunks=chunk_text(text),
            ).model_dump(),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        os.unlink(tmp.name)


@app.get("/health")
def health():
    return {
        "status": "ok" if PARSER_READY else "degraded",
        "parser": "markitdown" if PARSER_READY else "unavailable",
        "s3": BOTO_READY,
    }


@app.get("/")
def root():
    return {"service": "aios-docling", "version": "1.0.0", "docs": "/docs"}

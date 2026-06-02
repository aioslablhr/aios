#!/usr/bin/env python3
"""
AIOS Document Ingestion Pipeline.

Watches MinIO buckets for new files → docling → embed → Qdrant.
Can run in daemon mode (tail MinIO) or single-shot mode.

Usage:
  python3 ingest-file.py                          # daemon mode — watches MinIO
  python3 ingest-file.py --once                   # process all unprocessed files
  python3 ingest-file.py --file bucket/key.pdf    # process single file
"""

import os
import sys
import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest-file")

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    logger.error("boto3 required — pip install boto3")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None
    logger.error("requests required — pip install requests")
    sys.exit(1)

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "10.30.0.40:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
INPUT_BUCKET = os.environ.get("INPUT_BUCKET", "raw-uploads")

DOCLING_URL = os.environ.get("DOCLING_URL", "http://10.20.0.60:8000/v1")
QDRANT_HOST = os.environ.get("QDRANT_HOST", "10.30.0.20")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "aios_qdrant_2026")
EMBEDDING_URL = os.environ.get("EMBEDDING_URL", "http://10.40.0.10:4000/v1/embeddings")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_API_KEY = os.environ.get("EMBEDDING_API_KEY", "sk-aios-bifrost")

COLLECTION_NAME = "knowledge_chunks"

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)


def ensure_collection():
    resp = requests.put(
        f"http://{QDRANT_HOST}:6333/collections/{COLLECTION_NAME}",
        headers={"api-key": QDRANT_API_KEY, "Content-Type": "application/json"},
        json={
            "vectors": {"size": 768, "distance": "Cosine"},
            "optimizers_config": {"default_segment_number": 2},
        },
        timeout=10,
    )
    if resp.status_code == 200:
        logger.info(f"Collection '{COLLECTION_NAME}' ready")
    elif resp.status_code == 409:
        logger.info(f"Collection '{COLLECTION_NAME}' already exists")


def embed_text(text: str) -> list[float] | None:
    try:
        resp = requests.post(
            EMBEDDING_URL,
            headers={"Authorization": f"Bearer {EMBEDDING_API_KEY}", "Content-Type": "application/json"},
            json={"input": text, "model": EMBEDDING_MODEL},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["data"][0]["embedding"]
    except Exception as e:
        logger.warning(f"Embedding failed: {e}")
    return None


def index_to_qdrant(chunks: list[dict], filename: str):
    points = []
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        embedding = embed_text(text)
        if embedding is None:
            logger.warning(f"Chunk {i} of {filename} skipped — no embedding")
            continue

        point_id = hashlib.md5(f"{filename}:{i}".encode()).hexdigest()
        points.append({
            "id": point_id,
            "vector": embedding,
            "payload": {
                "text": text,
                "source": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "ingested_at": datetime.utcnow().isoformat(),
                **chunk.get("metadata", {}),
            },
        })

    if points:
        resp = requests.put(
            f"http://{QDRANT_HOST}:6333/collections/{COLLECTION_NAME}/points",
            headers={"api-key": QDRANT_API_KEY, "Content-Type": "application/json"},
            json={"points": points},
            timeout=30,
        )
        if resp.status_code == 200:
            logger.info(f"Indexed {len(points)} chunks from {filename}")
        else:
            logger.error(f"Qdrant upsert failed: {resp.text}")


def process_file(bucket: str, key: str):
    logger.info(f"Processing: {bucket}/{key}")

    resp = requests.post(
        f"{DOCLING_URL}/parse/minio",
        json={"bucket": bucket, "key": key, "delete_after": False},
        timeout=120,
    )

    if resp.status_code != 200 or resp.json().get("status") != "ok":
        logger.error(f"Docling failed for {key}: {resp.text}")
        return

    result = resp.json()["result"]
    chunks_data = [
        {"text": chunk, "metadata": {"content_type": result["content_type"]}}
        for chunk in result.get("chunks", [result["markdown"]])
    ]

    index_to_qdrant(chunks_data, key)
    logger.info(f"Done: {key} ({result['characters']} chars)")


def list_unprocessed(bucket: str) -> list[str]:
    try:
        resp = s3.list_objects_v2(Bucket=bucket)
        return [obj["Key"] for obj in resp.get("Contents", [])]
    except ClientError as e:
        logger.error(f"MinIO list error: {e}")
        return []


def daemon_loop(bucket: str, interval: int = 30):
    logger.info(f"Daemon mode — watching bucket '{bucket}' every {interval}s")
    seen = set()
    while True:
        files = list_unprocessed(bucket)
        for key in files:
            if key not in seen:
                process_file(bucket, key)
                seen.add(key)
        time.sleep(interval)


def main():
    bucket = sys.argv[sys.argv.index("--bucket") + 1] if "--bucket" in sys.argv else INPUT_BUCKET

    ensure_collection()

    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        parts = sys.argv[idx + 1].split("/", 1)
        process_file(parts[0], parts[1])
    elif "--once" in sys.argv:
        files = list_unprocessed(bucket)
        logger.info(f"Found {len(files)} unprocessed files in '{bucket}'")
        for key in files:
            process_file(bucket, key)
    else:
        daemon_loop(bucket)


if __name__ == "__main__":
    main()

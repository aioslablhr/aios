#!/usr/bin/env python3
"""
AIOS Knowledge Compiler — Daily consolidation pipeline.

Flow:
  1. Query mem0 for new memories since last run
  2. Query Qdrant for new document chunks since last run
  3. LLM summarizes and extracts patterns
  4. Writes/updates wiki/ markdown pages
  5. Prunes stale Qdrant vectors

Run: python3 compile-wiki.py [--force]
Schedule: cron daily at midnight
"""

import os
import sys
import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("compile-wiki")

CONFIG_PATH = Path(__file__).parent / "config.yaml"
WIKI_DIR = Path(__file__).parent / "wiki"
STATE_FILE = Path(__file__).parent / ".compile-state.json"

try:
    import yaml
except ImportError:
    yaml = None
    logger.warning("PyYAML not available — using env vars only")

try:
    import requests
except ImportError:
    requests = None
    logger.error("requests required — pip install requests")
    sys.exit(1)


def load_config() -> dict:
    if yaml and CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {
        "llm": {"base_url": os.environ.get("LLM_BASE_URL", "http://10.40.0.10:4000/v1"),
                "model": os.environ.get("LLM_MODEL", "gemma-4-31b"),
                "api_key": os.environ.get("LLM_API_KEY", "sk-aios-bifrost")},
        "qdrant": {"host": os.environ.get("QDRANT_HOST", "10.30.0.20"),
                   "api_key": os.environ.get("QDRANT_API_KEY", "aios_qdrant_2026")},
        "mem0": {"url": os.environ.get("MEM0_URL", "http://10.20.0.50:8000/v1")},
    }


def get_last_run() -> str:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f).get("last_run", "")
    return ""


def save_last_run():
    with open(STATE_FILE, "w") as f:
        json.dump({"last_run": datetime.now(timezone.utc).isoformat()}, f)


def query_mem0(config: dict, since: str) -> list[dict]:
    mem0_url = config.get("mem0", {}).get("url", "http://10.20.0.50:8000/v1")
    try:
        resp = requests.get(f"{mem0_url}/v1/memory", timeout=10)
        if resp.status_code == 503:
            logger.info("mem0 not ready (awaiting Bifrost/Ollama)")
            return []
        if resp.status_code == 200:
            return resp.json().get("memories", [])
    except requests.RequestException as e:
        logger.warning(f"mem0 query failed: {e}")
    return []


def query_qdrant(config: dict, since: str) -> list[dict]:
    qdrant_host = config.get("qdrant", {}).get("host", "10.30.0.20")
    qdrant_key = config.get("qdrant", {}).get("api_key", "aios_qdrant_2026")
    try:
        resp = requests.post(
            f"http://{qdrant_host}:6333/collections/knowledge_chunks/points/scroll",
            headers={"api-key": qdrant_key},
            json={"limit": 100, "with_payload": True},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("result", {}).get("points", [])
    except requests.RequestException as e:
        logger.warning(f"Qdrant query failed: {e}")
    return []


def summarize_with_llm(config: dict, memories: list[dict], chunks: list[dict]) -> str:
    llm_config = config.get("llm", {})
    base_url = llm_config.get("base_url", "http://10.40.0.10:4000/v1")
    model = llm_config.get("model", "gemma-4-31b")
    api_key = llm_config.get("api_key", "sk-aios-bifrost")

    mem_summary = json.dumps([m.get("memory", "") for m in memories[:50]], indent=2)
    chunk_summary = json.dumps([p.get("payload", {}).get("text", "")[:200] for p in chunks[:50]], indent=2)

    prompt = f"""You are the AIOS Knowledge Compiler. Analyze these new memories and document chunks,
then extract key facts, entities, patterns, and updates. Format as structured markdown.

NEW MEMORIES:
{mem_summary}

NEW DOCUMENTS:
{chunk_summary}

Output:
1. New entities discovered
2. Updated facts
3. Emerging patterns
4. Knowledge gaps
5. Suggested wiki page updates"""

    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.3, "max_tokens": 2000},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"LLM summarization failed: {e}")
    return "No new knowledge compiled."


def write_wiki_page(category: str, name: str, content: str):
    page_dir = WIKI_DIR / category
    page_dir.mkdir(parents=True, exist_ok=True)
    path = page_dir / f"{name}.md"
    with open(path, "w") as f:
        f.write(content)
    logger.info(f"Wiki page updated: {path.relative_to(WIKI_DIR.parent)}")


def main():
    force = "--force" in sys.argv
    config = load_config()
    last_run = get_last_run()

    logger.info(f"Knowledge Compiler starting (last run: {last_run or 'never'})")

    if not force and last_run:
        hours_since = (datetime.now(timezone.utc) - datetime.fromisoformat(last_run)).total_seconds() / 3600
        if hours_since < 1:
            logger.info(f"Last run was {hours_since:.1f}h ago — skipping (run with --force to override)")
            return

    memories = query_mem0(config, last_run)
    chunks = query_qdrant(config, last_run)
    logger.info(f"Found {len(memories)} new memories, {len(chunks)} new document chunks")

    if not memories and not chunks:
        logger.info("Nothing new to compile")
        save_last_run()
        return

    summary = summarize_with_llm(config, memories, chunks)
    logger.info(f"Compilation summary: {summary[:100]}...")

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    index_path = WIKI_DIR / "index.md"
    if index_path.exists():
        with open(index_path) as f:
            index_content = f.read()
        index_content = index_content.replace("{{DATE}}", date_str)
        with open(index_path, "w") as f:
            f.write(index_content)

    compilation_log = WIKI_DIR / "sources" / "compilation-log.md"
    with open(compilation_log, "a") as f:
        f.write(f"\n## Compilation {date_str}\n\n{summary}\n\n---\n")

    save_last_run()
    logger.info("Knowledge compilation complete")


if __name__ == "__main__":
    main()

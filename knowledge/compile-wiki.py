#!/usr/bin/env python3
"""
AIOS Knowledge Compiler — generates structured wiki pages from raw source documents.

Usage:
  python3 compile-wiki.py --company shin-travels

Flow:
  1. Reads raw documents from companies/{slug}/raw/
  2. Loads SCHEMA.md for behavioral rules
  3. Loads page-type templates from templates/
  4. Sends content to LLM via Bifrost → generates structured, interlinked wiki pages
  5. Writes to companies/{slug}/wiki/

Each company gets its own wiki. All follow same schema. All logged to Langfuse.
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("compile-wiki")

try:
    import yaml
except ImportError:
    yaml = None
    logger.warning("PyYAML not available")

try:
    import requests
except ImportError:
    requests = None  # type: ignore
    logger.error("requests required — pip install requests")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
COMPANIES_DIR = BASE_DIR / "companies"
SCHEMA_PATH = BASE_DIR / "SCHEMA.md"
CONFIG_PATH = BASE_DIR / "config.yaml"


def load_config() -> dict:
    if yaml and CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {
        "llm": {
            "base_url": os.environ.get("LLM_BASE_URL", "http://10.40.0.10:4000/v1"),
            "model": os.environ.get("LLM_MODEL", "gemma-4-31b"),
            "api_key": os.environ.get("LLM_API_KEY", "sk-aios-bifrost"),
        }
    }


def load_schema() -> str:
    if SCHEMA_PATH.exists():
        with open(SCHEMA_PATH) as f:
            return f.read()
    return ""


def load_template(name: str) -> str:
    path = TEMPLATES_DIR / name
    if path.exists():
        with open(path) as f:
            return f.read()
    return ""


def read_raw_docs(company_dir: Path) -> list[dict]:
    raw_dir = company_dir / "raw"
    if not raw_dir.exists():
        logger.warning(f"No raw/ directory at {raw_dir}")
        return []
    docs = []
    for fpath in sorted(raw_dir.glob("*.md")):
        with open(fpath) as f:
            content = f.read().strip()
        docs.append({"filename": fpath.name, "title": fpath.stem, "content": content})
        logger.info(f"  Loaded raw doc: {fpath.name} ({len(content)} chars)")
    return docs


def read_existing_wiki(company_dir: Path) -> dict:
    wiki_dir = company_dir / "wiki"
    existing = {"concepts": {}, "entities": {}, "sources": {}}
    if not wiki_dir.exists():
        return existing
    for category in existing:
        cat_dir = wiki_dir / category
        if not cat_dir.exists():
            continue
        for fpath in cat_dir.glob("*.md"):
            with open(fpath) as f:
                existing[category][fpath.stem] = f.read()
    return existing


def call_llm(config: dict, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    llm = config.get("llm", {})
    base_url = llm.get("base_url", "http://10.40.0.10:4000/v1")
    model = llm.get("model", "gemma-4-31b")
    api_key = llm.get("api_key", "sk-aios-bifrost")
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": 4000,
            },
            timeout=120,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            logger.error(f"LLM call failed: {resp.status_code} {resp.text[:200]}")
            return ""
    except Exception as e:
        logger.error(f"LLM call error: {e}")
        return ""


def compile_company(config: dict, slug: str):
    logger.info(f"=== Compiling wiki for company: {slug} ===")
    company_dir = COMPANIES_DIR / slug
    if not company_dir.exists():
        logger.error(f"Company directory not found: {company_dir}")
        return
    schema = load_schema()
    if not schema:
        logger.error("SCHEMA.md not found — cannot compile without rules")
        return
    templates = {
        "concept": load_template("concept.md"),
        "entity": load_template("entity.md"),
        "source": load_template("source.md"),
        "index": load_template("index.md"),
    }
    if not all(templates.values()):
        logger.error("One or more templates missing from knowledge/templates/")
        return
    raw_docs = read_raw_docs(company_dir)
    if not raw_docs:
        logger.warning("No raw documents found — nothing to compile")
        return
    existing_wiki = read_existing_wiki(company_dir)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    system_prompt = (
        "You are the AIOS Knowledge Compiler. You generate structured wiki pages "
        "from raw company documents.\n\n"
        f"{schema}\n\n"
        "You MUST produce output in the following format, strictly using the templates "
        "provided. Replace every `{PLACEHOLDER}` with real content.\n\n"
        "Output format:\n"
        "---CONCEPT---\n"
        "filename: {slug}.md\n"
        f"{templates['concept']}\n\n"
        "---ENTITY---\n"
        "filename: {slug}.md\n"
        f"{templates['entity']}\n\n"
        "---SOURCE---\n"
        "filename: {slug}.md\n"
        f"{templates['source']}\n\n"
        "---INDEX---\n"
        f"filename: index.md\n"
        f"{templates['index']}\n"
    )
    user_prompt = (
        f"Company: {slug}\n"
        f"Date: {date_str}\n\n"
        "Raw source documents:\n"
    )
    for doc in raw_docs:
        user_prompt += f"\n### File: {doc['filename']}\n{doc['content']}\n"
    if any(existing_wiki.values()):
        user_prompt += "\nExisting wiki pages (update these, don't duplicate):\n"
        for category, pages in existing_wiki.items():
            for name, content in pages.items():
                user_prompt += f"\n### {category}/{name}.md\n{content[:500]}...\n"
    logger.info("Sending to LLM for compilation...")
    result = call_llm(config, system_prompt, user_prompt, temperature=0.3)
    if not result:
        logger.error("LLM returned empty response")
        return
    wiki_dir = company_dir / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    for cat in ("concepts", "entities", "sources"):
        (wiki_dir / cat).mkdir(exist_ok=True)
    sections = result.split("---")
    current_type = None
    current_filename = None
    current_content = []
    page_count = 0
    for section in sections:
        section = section.strip()
        if section.startswith("CONCEPT"):
            if current_filename and current_content:
                save_wiki_page(wiki_dir, current_type, current_filename, current_content)
                page_count += 1
            current_type = "concepts"
            current_content = []
            current_filename = None
        elif section.startswith("ENTITY"):
            if current_filename and current_content:
                save_wiki_page(wiki_dir, current_type, current_filename, current_content)
                page_count += 1
            current_type = "entities"
            current_content = []
            current_filename = None
        elif section.startswith("SOURCE"):
            if current_filename and current_content:
                save_wiki_page(wiki_dir, current_type, current_filename, current_content)
                page_count += 1
            current_type = "sources"
            current_content = []
            current_filename = None
        elif section.startswith("INDEX"):
            if current_filename and current_content:
                save_wiki_page(wiki_dir, current_type, current_filename, current_content)
                page_count += 1
            current_type = None
            current_content = []
            current_filename = None
        elif section.startswith("filename:"):
            current_filename = section.split("filename:")[1].strip()
        else:
            if section and current_content is not None:
                current_content.append(section)
    if current_filename and current_content:
        save_wiki_page(wiki_dir, current_type, current_filename, current_content)
        page_count += 1
    compile_state = company_dir / ".compile-state.json"
    with open(compile_state, "w") as f:
        json.dump({"last_run": datetime.now(timezone.utc).isoformat(), "page_count": page_count}, f)
    logger.info(f"Compilation complete — {page_count} pages written to {wiki_dir}")


def save_wiki_page(wiki_dir: Path, category: str | None, filename: str, content_lines: list[str]):
    if not category or not filename:
        return
    content = "\n".join(content_lines).strip()
    if not content:
        return
    cat_dir = wiki_dir / category
    cat_dir.mkdir(exist_ok=True)
    path = cat_dir / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"  Wrote: {category}/{filename} ({len(content)} chars)")


def main():
    parser = argparse.ArgumentParser(description="AIOS Knowledge Compiler")
    parser.add_argument("--company", required=True, help="Company slug (e.g. shin-travels)")
    args = parser.parse_args()
    config = load_config()
    compile_company(config, args.company)


if __name__ == "__main__":
    main()

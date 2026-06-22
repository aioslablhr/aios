"""Wiki Knowledge Loader

Reads a company's compiled wiki markdown files and formats them into a
single text block for injection into the LLM system prompt.

Directory structure expected:
    /knowledge/{company}/wiki/
        index.md
        concepts/*.md
        entities/*.md
        sources/*.md
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from loguru import logger


WIKI_BASE = Path("/knowledge")


def load_company_wiki(company: str) -> str:
    """Load and format a company's complete wiki knowledge base.

    Args:
        company: Company identifier matching the wiki directory name
                (e.g. "imperium", "shin-travels")

    Returns:
        Formatted string with all wiki content, or empty string if
        no wiki is found for this company.
    """
    wiki_dir = WIKI_BASE / company / "wiki"

    if not wiki_dir.exists() or not wiki_dir.is_dir():
        logger.warning(f"Wiki directory not found: {wiki_dir}")
        return ""

    sections: list[str] = []
    sections.append(_read_file_compact(wiki_dir / "index.md"))

    sections.append("\n=== COMPANY ENTITIES ===")
    for f in sorted((wiki_dir / "entities").glob("*.md")):
        sections.append(_read_file_compact(f))

    sections.append("\n=== SERVICES & CONCEPTS ===")
    for f in sorted((wiki_dir / "concepts").glob("*.md")):
        sections.append(_read_file_compact(f))

    sources_dir = wiki_dir / "sources"
    if sources_dir.exists():
        sections.append("\n=== SOURCES ===")
        for f in sorted(sources_dir.glob("*.md")):
            sections.append(_read_file_compact(f))

    result = "\n".join(sections).strip()
    logger.info(f"Loaded wiki for '{company}': {len(result)} chars from {len(sections)} sections")
    return result


def _read_file_compact(path: Path) -> str:
    """Read a markdown file, strip front matter and return compact content."""
    if not path.exists():
        return ""

    content = path.read_text(encoding="utf-8")

    # Strip YAML front matter (between --- delimiters)
    content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, count=1, flags=re.DOTALL)

    # Remove markdown image references (they add noise)
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)

    # Strip heading markers but keep heading text (sections are clear enough)
    content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)

    # Remove wiki-style internal links keeping the text
    # [[link]] → link, [[link|text]] → text
    content = re.sub(r"\[\[([^\]|]+)\]\]", r"\1", content)
    content = re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", content)

    # Remove regular markdown links keeping the text
    # [text](url) → text
    content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)

    # Collapse multiple blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content.strip()

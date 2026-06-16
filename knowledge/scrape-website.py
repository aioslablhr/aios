#!/usr/bin/env python3
"""
AIOS Website Scraper — converts a company website into raw markdown files.

Usage:
  python3 scrape-website.py --url https://shintravels.co.uk --out companies/shin-travels/raw/

Output:
  Raw markdown files saved to --out directory, one per page.
  These go into a company's raw/ folder for the wiki compiler.
"""

import os
import sys
import argparse
import logging
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scrape-website")

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    logger.error("Missing dependencies: pip install requests beautifulsoup4")
    sys.exit(1)


def url_to_filename(url: str, base_domain: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "index"
    parts = [p for p in path.split("/") if p]
    slug = "-".join(parts)
    slug = re.sub(r"[^a-zA-Z0-9\-]", "", slug)
    return slug if slug else "index"


def html_to_markdown(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    title = re.sub(r"\s+", " ", title)
    body = soup.find("main") or soup.find("article") or soup.find("body") or soup
    lines = []
    for el in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "table", "tr", "th", "td"]):
        tag = el.name
        text = el.get_text(strip=True)
        if not text:
            continue
        if tag == "h1":
            lines.append(f"\n# {text}")
        elif tag == "h2":
            lines.append(f"\n## {text}")
        elif tag == "h3":
            lines.append(f"\n### {text}")
        elif tag == "li":
            lines.append(f"- {text}")
        elif tag in ("th", "td"):
            pass
        elif tag == "tr":
            pass
        elif tag == "p":
            lines.append(f"\n{text}")
    content = "\n".join(lines)
    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    return f"# {title}\n\n> Source: {url}\n\n{content}"


def scrape_site(base_url: str, output_dir: Path):
    visited = set()
    to_visit = {base_url}
    base_domain = urlparse(base_url).netloc
    output_dir.mkdir(parents=True, exist_ok=True)

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "AIOS-Scraper/1.0"})
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"Failed {url}: {e}")
            continue
        filename = url_to_filename(url, base_domain)
        md = html_to_markdown(resp.text, url)
        filepath = output_dir / f"{filename}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
        logger.info(f"Saved {filepath.name} ({len(md)} chars)")
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full = urljoin(url, href)
            parsed = urlparse(full)
            if parsed.netloc == base_domain and parsed.scheme in ("http", "https") and full not in visited:
                to_visit.add(full)

    logger.info(f"Done. Scraped {len(visited)} pages → {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="AIOS Website Scraper")
    parser.add_argument("--url", required=True, help="Website URL to scrape")
    parser.add_argument("--out", required=True, help="Output directory for raw markdown")
    args = parser.parse_args()
    scrape_site(args.url.rstrip("/"), Path(args.out))


if __name__ == "__main__":
    main()

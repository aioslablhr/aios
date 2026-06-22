"""Scrape shintravels.co.uk with browser User-Agent."""
import requests, os, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

base = 'https://shintravels.co.uk'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
out_dir = '/app/companies/shin-travels/raw'
os.makedirs(out_dir, exist_ok=True)

visited = set()

def save_page(url, content):
    path = urlparse(url).path.strip('/').replace('/', '-') or 'index'
    if not path.endswith('.md'):
        path += '.md'
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    with open(os.path.join(out_dir, path), 'w', encoding='utf-8') as f:
        f.write(f'# {path}\n\nURL: {url}\n\n{text}')
    print(f'  Saved: {path} ({len(text)} chars)')

# Scrape main page
resp = requests.get(base, headers=headers, timeout=20)
visited.add(resp.url)
save_page(resp.url, resp.text)

# Find links
soup = BeautifulSoup(resp.text, 'html.parser')
for a in soup.find_all('a', href=True):
    url = urljoin(base, a['href'])
    if url.startswith(base) and url not in visited and '#' not in url:
        try:
            p = requests.get(url, headers=headers, timeout=20)
            visited.add(p.url)
            save_page(p.url, p.text)
        except Exception as e:
            print(f'  Skipped: {url} - {e}')

print(f'Done. Scraped {len(visited)} pages')

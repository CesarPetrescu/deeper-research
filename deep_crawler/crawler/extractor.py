import re
import requests
from readability import Document
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0 Safari/537.36"
)

def simple_extract(url, timeout=15):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    doc = Document(resp.text)
    title = doc.short_title() or url
    clean_html = doc.summary()
    soup = BeautifulSoup(clean_html, "lxml")
    text = soup.get_text("\n")
    return {
        "url": url,
        "title": title,
        "markdown": f"# {title}\n\n{text[:4000]}",
    }

def looks_dynamic(html):
    return bool(re.search(r"<script[^>]+src=", html, re.I))

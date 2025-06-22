#!/usr/bin/env python3
"""
deep_search_pipeline.py
────────────────────────────────────────────────────────────────────────────
End‑to‑end research assistant that turns a *natural‑language question* into
a fully‑cited Markdown report, via:

1.  Planning + keyword extraction (LLM → XML list)
2.  Web search through **SearXNG**  (`/search?format=json`)
3.  Site crawling with **Firecrawl** (self‑hosted at http://localhost:3002)
4.  Embedding all pages with an OpenAI‑compatible endpoint
5.  Vector search + section‑wise summarisation (Mistral)
6.  Final Markdown assembly + bibliography

No heavy frameworks; only standard Python + a few light deps.

Copyright © 2025  – Apache‑2.0
"""

import os, sys, json, time, textwrap, uuid
from pathlib import Path
from typing import List, Dict, Tuple
import requests, faiss, numpy as np
from tenacity import retry, stop_after_attempt, wait_fixed
from tqdm import tqdm
import xml.etree.ElementTree as ET

# ──────────────────────────────────────────────────────────────
# 0. Configuration – via env vars so nothing is hard‑coded
# ──────────────────────────────────────────────────────────────

CFG = {
    # Local LM Studio endpoint (Mistral‐instruct)
    "OPENAI_API_BASE": os.getenv("OPENAI_API_BASE", "http://192.168.100.199:5515/v1"),
    "OPENAI_API_KEY":  os.getenv("OPENAI_API_KEY", "none"),          # LM Studio ignores key
    "CHAT_MODEL":      os.getenv("CHAT_MODEL", "mistral-small-3.2-24b-instruct-2506"),
    "EMBED_MODEL":     os.getenv("EMBED_MODEL", "text-embedding-granite-embedding-278m-multilingual"),

    # SearXNG instance  (⚠️  MUST include /search on every query)
    "SEARX_URL":       os.getenv("SEARX_URL", "https://searx.sprk.ro/search"),

    # Self‑hosted Firecrawl API
    "FIRECRAWL_URL":   os.getenv("FIRECRAWL_URL", "http://localhost:3002"),

    # Tunables
    "URLS_PER_KEYWORD": int(os.getenv("URLS_PER_KEYWORD", 4)),
    "CRAWL_LIMIT":      int(os.getenv("CRAWL_LIMIT", 8)),   # pages per seed URL
    "SNIPPETS_PER_SEC": int(os.getenv("SNIPPETS_PER_SEC", 8))
}

# ──────────────────────────────────────────────────────────────
# 1. LLM helpers (OpenAI‑compatible REST)
# ──────────────────────────────────────────────────────────────

import openai

import openai

# Ensure the base URL ends with a slash for proper URL construction
base_url = CFG["OPENAI_API_BASE"]
if not base_url.endswith('/'):
    base_url += '/'

client = openai.OpenAI(
    api_key=CFG["OPENAI_API_KEY"],
    base_url=base_url
)

def test_api_connection():
    """Test if the OpenAI-compatible API is reachable and working"""
    try:
        # Try a simple test request
        response = requests.get(f"{CFG['OPENAI_API_BASE']}/models", timeout=10)
        if response.status_code == 200:
            print(f"✓ API endpoint reachable at {CFG['OPENAI_API_BASE']}")
            models = response.json().get("data", [])
            if models:
                print(f"✓ Found {len(models)} available models")
                # Check if our target model is available
                model_ids = [m.get("id", "") for m in models]
                if CFG["CHAT_MODEL"] in model_ids:
                    print(f"✓ Target model '{CFG['CHAT_MODEL']}' is available")
                else:
                    print(f"⚠ Target model '{CFG['CHAT_MODEL']}' not found")
                    print(f"  Available models: {model_ids[:5]}...")  # Show first 5
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        return False

def llm(system: str, user: str, model=CFG["CHAT_MODEL"], max_tokens=1024) -> str:
    try:
        r = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}]
        )
        
        if not hasattr(r, 'choices') or not r.choices:
            raise ValueError("No choices returned from LLM")
        
        if r.choices[0].message.content is None:
            raise ValueError("LLM returned None content")
            
        return r.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        print(f"   Model: {model}")
        print(f"   API Base: {base_url}")
        raise

def embed(texts: List[str], model=CFG["EMBED_MODEL"]) -> np.ndarray:
    out = client.embeddings.create(model=model, input=texts)
    return np.array([d.embedding for d in out.data], dtype="float32")

# ──────────────────────────────────────────────────────────────
# 2. Plan + keyword list as XML
# ──────────────────────────────────────────────────────────────

SYS_PLANNER = "You are an expert research planner. Return outline + XML keyword list."
USR_PLANNER = """\
Topic: {topic}

1. Give a Markdown outline (3–6 H2 sections).
2. Provide 10–15 STEM‑specific search phrases wrapped in:
<keywords><k>…</k>…</keywords>
"""

def plan_and_keywords(topic: str) -> Tuple[str, List[str]]:
    out = llm(SYS_PLANNER, USR_PLANNER.format(topic=topic), max_tokens=800)
    outline, xml_raw = out.split("<keywords", 1)
    xml = "<keywords" + xml_raw
    root = ET.fromstring(xml)
    keywords = [k.text.strip() for k in root.findall("./k") if k.text]
    return outline.strip(), keywords

# ──────────────────────────────────────────────────────────────
# 3. SearX search
# ──────────────────────────────────────────────────────────────

def searx(q: str, n=CFG["URLS_PER_KEYWORD"]) -> List[str]:
    r = requests.get(CFG["SEARX_URL"],
                     params={"q": q, "format": "json", "language": "en"},
                     timeout=30)
    r.raise_for_status()
    hits = r.json().get("results", [])
    return [h["url"] for h in hits[:n]]

# ──────────────────────────────────────────────────────────────
# 4. Firecrawl wrapper
# ──────────────────────────────────────────────────────────────

@retry(stop=stop_after_attempt(25), wait=wait_fixed(2))
def _wait(job_id: str) -> Dict:
    js = requests.get(f"{CFG['FIRECRAWL_URL']}/v1/crawl/{job_id}", timeout=60).json()
    print(f"Job {job_id} status: {js.get('status', 'unknown')}")
    
    if js["status"] == "failed":
        print(f"Job {job_id} failed: {js}")
        raise RuntimeError(f"Crawl job failed: {js}")
    
    if js["status"] != "completed":
        print(f"Job {job_id} not ready, waiting...")
        raise RuntimeError("Not ready")
    
    return js

def crawl(url: str, limit=CFG["CRAWL_LIMIT"]) -> List[Dict]:
    """
    Crawl a URL using simple HTTP requests with basic text extraction
    """
    return simple_fetch_fallback(url)

def simple_fetch_fallback(url: str) -> List[Dict]:
    """
    Simple fallback that fetches a URL and extracts basic text content
    """
    try:
        import re
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        # Create a simple page structure
        title = soup.title.string if soup.title else url.split('/')[-1]
        
        return [{
            "url": url,
            "title": title,
            "markdown": f"# {title}\n\n{text[:4000]}"  # Limit content length
        }]
        
    except Exception as e:
        print(f"Fallback failed for {url}: {e}")
        return []

def _wait_with_timeout(job_id: str, max_wait=30) -> Dict:
    """
    Wait for a crawl job with a maximum timeout
    """
    import time
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            js = requests.get(f"{CFG['FIRECRAWL_URL']}/v1/crawl/{job_id}", timeout=5).json()
            
            if js["status"] == "failed":
                raise RuntimeError(f"Crawl job failed: {js}")
            
            if js["status"] == "completed":
                return js
                
            time.sleep(2)  # Wait 2 seconds before checking again
            
        except requests.RequestException:
            break
    
    raise RuntimeError("Crawl job timed out")

# ──────────────────────────────────────────────────────────────
# 5. Build FAISS index for retrieval
# ──────────────────────────────────────────────────────────────

def build_index(pages: List[Dict]) -> Tuple[faiss.IndexFlatIP, List[str]]:
    texts = [p["markdown"][:4096] for p in pages]  # clip
    vecs  = embed(texts)
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    return index, texts

def top_k(index, texts, query, k=CFG["SNIPPETS_PER_SEC"]):
    qv = embed([query])
    faiss.normalize_L2(qv)
    D, I = index.search(qv, k)
    snips = []
    for idx in I[0]:
        snippet = textwrap.shorten(texts[idx], 350)
        snips.append((idx+1, snippet))
    return snips

# ──────────────────────────────────────────────────────────────
# 6. Section‑wise summary writer
# ──────────────────────────────────────────────────────────────

SYS_SUM = ("You are a domain expert. Using ONLY the numbered snippets, "
           "draft the section, then bullet key takeaways, citing like [1].")

TMPL_SEC = """SECTION: {heading}

Snippets:
{snips}

Write ≈200 words, then • key takeaways. Use citations.
"""

def write_section(heading, index, texts):
    sn = top_k(index, texts, heading)
    snips_text = "\n".join(f"[{cid}] {txt}" for cid, txt in sn)
    prompt = TMPL_SEC.format(heading=heading, snips=snips_text)
    return llm(SYS_SUM, prompt, max_tokens=400)

# ──────────────────────────────────────────────────────────────
# 7. Main orchestration
# ──────────────────────────────────────────────────────────────

def run_research(query: str) -> str:
    outline, kws = plan_and_keywords(query)
    print("Keywords:", ", ".join(kws))

    # Gather URLs
    urls = []
    for kw in kws:
        urls.extend(searx(kw))
    urls = list(dict.fromkeys(urls))    # dedupe

    # Crawl
    pages = []
    for u in tqdm(urls, desc="Crawling"):
        try:
            pages += crawl(u)
        except Exception as e:
            print("❌", u, e)

    if not pages:
        raise RuntimeError("No pages crawled.")

    # Index
    index, texts = build_index(pages)

    # Assemble doc
    doc = [f"# {query}", "", "## Outline", outline, ""]
    sections = [l.strip("# ").strip()
                for l in outline.splitlines() if l.startswith("##")]

    for h in sections:
        doc.append(f"## {h}")
        doc.append(write_section(h, index, texts))
        doc.append("")

    # Bibliography
    doc.append("## References")
    for i, p in enumerate(pages, 1):
        title = p["markdown"].splitlines()[0].lstrip("# ").strip()
        doc.append(f"[{i}] {title} — {p['url']}")
    return "\n".join(doc)

# ──────────────────────────────────────────────────────────────
# 8. CLI
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Script starting...")
    
    if len(sys.argv) < 2:
        print("Usage: deep_search_pipeline.py \"Your research question\"")
        sys.exit(1)

    print(f"Arguments: {sys.argv}")
    print(f"Query: {sys.argv[1]}")

    # Test API connection first
    print("Testing API connection...")
    if not test_api_connection():
        print("❌ API connection failed. Please check your configuration.")
        sys.exit(1)

    print("Starting research...")
    md = run_research(sys.argv[1])
    outfile = Path(f"report_{uuid.uuid4().hex[:8]}.md")
    outfile.write_text(md, encoding="utf-8")
    print("✔  Report saved to", outfile)

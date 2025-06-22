Below is a **minimal but complete repo skeleton** that implements the “next‑gen” agent using **only Firecrawl**.
Each code block is a file – copy them into the directory tree as shown.

```
deep_crawler/
│  config.toml
│  cli.py
├─ crawler/
│  firecrawl_async.py
│  extractor.py
├─ indexing/
│  embed_cache.py
│  faiss_store.py
└─ llm/
   core.py
   planner.py
   summariser.py
   verifier.py
```

---

### `config.toml`

```toml
[api]
openai_base   = "http://192.168.100.199:5515/v1"
openai_key    = "none"
chat_model    = "mistral-small-3.2-24b-instruct-2506"
embed_model   = "text-embedding-granite-embedding-278m-multilingual"

[firecrawl]
base_url      = "http://localhost:3002"
concurrency   = 8            # async tasks
limit_per_url = 8            # pages per seed

[search]
searx_url         = "https://searx.sprk.ro/search"
urls_per_keyword  = 4

[index]
snippets_per_sec  = 8
```

---

### `llm/core.py`

```python
import toml, hashlib, functools
from pathlib import Path
from openai import OpenAI, OpenAIError

CFG = toml.load(Path(__file__).parents[1] / "config.toml")

client = OpenAI(base_url=CFG["api"]["openai_base"],
                api_key =CFG["api"]["openai_key"])

def chat(system, user, max_tokens=512, model=None):
    model = model or CFG["api"]["chat_model"]
    try:
        r = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,
            messages=[{"role":"system","content":system},
                      {"role":"user",  "content":user}]
        )
        return r.choices[0].message.content.strip()
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI chat error: {e}")

@functools.lru_cache(maxsize=1024)
def embed(text, model=None):
    model = model or CFG["api"]["embed_model"]
    r = client.embeddings.create(model=model, input=[text])
    return r.data[0].embedding, hashlib.md5(text.encode()).hexdigest()[:8]
```

---

### `crawler/extractor.py`

```python
import re, requests, hashlib
from readability import Document
from bs4 import BeautifulSoup

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/122.0 Safari/537.36")

def simple_extract(url, timeout=15):
    resp = requests.get(url, headers={"User-Agent":USER_AGENT},
                        timeout=timeout)
    resp.raise_for_status()
    doc = Document(resp.text)
    title = doc.short_title() or url
    clean_html = doc.summary()
    soup = BeautifulSoup(clean_html, "lxml")
    text = soup.get_text("\n")
    return {
        "url": url,
        "title": title,
        "markdown": f"# {title}\n\n{text[:4000]}"  # clip long pages
    }

def looks_dynamic(html):
    return bool(re.search(r"<script[^>]+src=", html, re.I))
```

---

### `crawler/firecrawl_async.py`

```python
import asyncio, aiohttp, time, hashlib
from .extractor import simple_extract, looks_dynamic
from pathlib import Path
import toml, json

CFG = toml.load(Path(__file__).parents[2] / "config.toml")
FC  = CFG["firecrawl"]["base_url"]

async def _fc_submit(session, url, limit):
    r = await session.post(f"{FC}/v1/crawl",
                           json={"url":url, "limit":limit})
    js = await r.json()
    return js["id"]

async def _fc_poll(session, jid, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        r = await session.get(f"{FC}/v1/crawl/{jid}")
        js = await r.json()
        if js["status"] == "completed":
            return js["pages"]
        if js["status"] == "failed":
            raise RuntimeError("Firecrawl job failed")
        await asyncio.sleep(2)
    raise TimeoutError("Firecrawl job timeout")

async def _handle_one(session, url, limit):
    try:
        jid = await _fc_submit(session, url, limit)
        return await _fc_poll(session, jid)
    except Exception:
        # static fallback
        return [simple_extract(url)]

async def crawl_urls(urls, limit=None, concurrency=None):
    limit        = limit or CFG["firecrawl"]["limit_per_url"]
    concurrency  = concurrency or CFG["firecrawl"]["concurrency"]
    sem          = asyncio.Semaphore(concurrency)
    pages        = []

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as s:
        async def worker(u):
            async with sem:
                try:
                    return await _handle_one(s, u, limit)
                except Exception:
                    return []

        tasks = [worker(u) for u in urls]
        for coro in asyncio.as_completed(tasks):
            pages += await coro
    return pages
```

---

### `indexing/embed_cache.py`

```python
import sqlite3, pickle, hashlib, os
from pathlib import Path
from llm.core import embed

DB_PATH = Path(__file__).parent / "embeddings.sqlite"
con = sqlite3.connect(DB_PATH)
con.execute("CREATE TABLE IF NOT EXISTS vecs"
            "(hash TEXT PRIMARY KEY, vec BLOB)")
con.commit()

def get_vector(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    cur = con.execute("SELECT vec FROM vecs WHERE hash=?", (h,))
    row = cur.fetchone()
    if row:
        return pickle.loads(row[0])

    vec, _ = embed(text)
    con.execute("INSERT OR REPLACE INTO vecs VALUES (?,?)",
                (h, pickle.dumps(vec)))
    con.commit()
    return vec
```

---

### `indexing/faiss_store.py`

```python
import faiss, numpy as np, hashlib, pickle, os
from pathlib import Path
from .embed_cache import get_vector

def build(texts):
    vecs = np.vstack([get_vector(t) for t in texts]).astype("float32")
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    return index

def save(index, path):
    faiss.write_index(index, str(path))

def load(path):
    return faiss.read_index(str(path))
```

---

### `llm/planner.py`

```python
from llm.core import chat
import xml.etree.ElementTree as ET

SYS = "You are a meticulous research planner. Return outline + XML keywords."
USR = """Topic: {q}

1. Output a Markdown outline with 3–6 H2 sections.
2. Provide 8–12 search keywords wrapped in:
<keywords><k>…</k></keywords>
"""

def plan(query):
    out = chat(SYS, USR.format(q=query), max_tokens=800)
    outline, xml_raw = out.split("<keywords", 1)
    root = ET.fromstring("<keywords" + xml_raw)
    kws  = [k.text.strip() for k in root.findall("./k") if k.text]
    return outline.strip(), kws
```

---

### `llm/summariser.py`

```python
from llm.core import chat
import toml, re, textwrap, faiss, numpy as np
from pathlib import Path
from indexing.embed_cache import get_vector

CFG = toml.load(Path(__file__).parents[2] / "config.toml")

SYS = ("You are a domain expert. Using ONLY these numbered snippets, "
       "write the section (~180 words) then bullet key take‑aways. "
       "Cite sources like [42].")

TMPL = """SECTION: {title}

Snippets:
{snips}

"""

def rank(index, texts, query, k):
    qv = get_vector(query)
    qv = np.array([qv], dtype="float32")
    faiss.normalize_L2(qv)
    _, I = index.search(qv, k)
    return I[0]

def summarise_section(title, index, texts):
    I = rank(index, texts, title, CFG["index"]["snippets_per_sec"])
    sn = "\n".join(f"[{i+1}] {textwrap.shorten(texts[i], 300)}" for i in I)
    return chat(SYS, TMPL.format(title=title, snips=sn), max_tokens=400)
```

---

### `llm/verifier.py`

```python
import re

def dangling_citations(markdown, id_set):
    cites = set(int(m) for m in re.findall(r"\[(\d+)]", markdown))
    return cites - id_set
```

---

### `cli.py`

```python
#!/usr/bin/env python3
import toml, requests, hashlib, asyncio, textwrap
from pathlib import Path
from tqdm import tqdm
from crawler.firecrawl_async import crawl_urls
from llm import planner, summariser
from indexing import faiss_store
from crawler.extractor import simple_extract
from llm.verifier import dangling_citations

CFG = toml.load(Path(__file__).parent / "config.toml")

def searx(q, n):
    r = requests.get(CFG["search"]["searx_url"],
                     params={"q":q, "format":"json", "language":"en"},
                     timeout=15).json()
    return [hit["url"] for hit in r.get("results", [])[:n]]

def main(question: str):
    outline, kws = planner.plan(question)
    print("· Keywords:", ", ".join(kws))

    urls = []
    for kw in kws:
        urls += searx(kw, CFG["search"]["urls_per_keyword"])
    urls = list(dict.fromkeys(urls))     # dedupe

    pages = asyncio.run(crawl_urls(urls))
    if not pages:
        raise RuntimeError("No pages scraped.")

    texts = [p["markdown"][:4096] for p in pages]
    index = faiss_store.build(texts)

    doc = [f"# {question}", "", "## Outline", outline, ""]
    sections = [l.strip("# ").strip() for l in outline.splitlines()
                if l.startswith("##")]

    for sec in sections:
        doc.append(f"## {sec}")
        doc.append(summariser.summarise_section(sec, index, texts))
        doc.append("")

    doc.append("## References")
    for i, p in enumerate(pages, 1):
        title = p["title"]
        doc.append(f"[{i}] {title} — {p['url']}")

    md = "\n".join(doc)
    dangling = dangling_citations(md, set(range(1, len(pages)+1)))
    if dangling:
        print("⚠ dangling cites", dangling)

    out = Path(f"report_{hashlib.md5(question.encode()).hexdigest()[:8]}.md")
    out.write_text(md, encoding="utf-8")
    print("✓ Report written to", out)

if __name__ == "__main__":
    import sys, textwrap
    if len(sys.argv) < 2:
        print("Usage: cli.py \"research question\"")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))
```

---

### Install deps & run

```bash
pip install aiohttp readability-lxml beautifulsoup4 requests tqdm tenacity faiss-cpu numpy openai toml
export OPENAI_API_BASE="http://192.168.100.199:5515/v1"
python cli.py "Future of superconductivity in graphene devices"
```

This stripped‑down stack:

* **Search** via SearXNG
* **Async Firecrawl** (with readability fallback)
* **SQLite‑cached embeddings**
* **FAISS retrieval + Mistral summaries**
* **Markdown report** with verified citations


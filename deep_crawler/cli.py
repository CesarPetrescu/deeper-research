#!/usr/bin/env python3
import toml
import requests
import hashlib
import asyncio
import textwrap
from pathlib import Path
from tqdm import tqdm
from crawler.firecrawl_async import crawl_urls
from llm import planner, summariser
from indexing import faiss_store
from crawler.extractor import simple_extract
from llm.verifier import dangling_citations

CFG = toml.load(Path(__file__).parent / "config.toml")

def searx(q, n):
    r = requests.get(
        CFG["search"]["searx_url"],
        params={"q": q, "format": "json", "language": "en"},
        timeout=15,
    ).json()
    return [hit["url"] for hit in r.get("results", [])[:n]]

def main(question: str):
    outline, kws = planner.plan(question)
    print("· Keywords:", ", ".join(kws))

    urls = []
    for kw in kws:
        urls += searx(kw, CFG["search"]["urls_per_keyword"])
    urls = list(dict.fromkeys(urls))  # dedupe

    pages = asyncio.run(crawl_urls(urls))
    if not pages:
        raise RuntimeError("No pages scraped.")

    texts = [p["markdown"][:4096] for p in pages]
    index = faiss_store.build(texts)

    doc = [f"# {question}", "", "## Outline", outline, ""]
    sections = [l.strip("# ").strip() for l in outline.splitlines() if l.startswith("##")]

    for sec in sections:
        doc.append(f"## {sec}")
        doc.append(summariser.summarise_section(sec, index, texts))
        doc.append("")

    doc.append("## References")
    for i, p in enumerate(pages, 1):
        title = p["title"]
        doc.append(f"[{i}] {title} — {p['url']}")

    md = "\n".join(doc)
    dangling = dangling_citations(md, set(range(1, len(pages) + 1)))
    if dangling:
        print("⚠ dangling cites", dangling)

    out = Path(f"report_{hashlib.md5(question.encode()).hexdigest()[:8]}.md")
    out.write_text(md, encoding="utf-8")
    print("✓ Report written to", out)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: cli.py \"research question\"")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))

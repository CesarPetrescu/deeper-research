#!/usr/bin/env python3
import toml
import requests
import hashlib
import asyncio
import textwrap
from pathlib import Path
from tqdm import tqdm
from deep_crawler.crawler.firecrawl_async import crawl_urls

try:
    # Prefer enhanced planner and summariser with LangChain features
    from deep_crawler.llm.enhanced_planner import plan_with_sections
    from deep_crawler.llm.enhanced_summariser import summarise_section
    ENHANCED = True
except ImportError:
    # Fallback to basic implementations if enhanced modules are unavailable
    from deep_crawler.llm import planner, summariser

    def plan_with_sections(question: str):
        """Basic outline planning with section extraction."""
        outline, kws = planner.plan(question)
        sections = [
            line.strip("# ").strip()
            for line in outline.splitlines()
            if line.startswith("## ")
        ]
        return outline, kws, sections

    summarise_section = summariser.summarise_section
    ENHANCED = False
from deep_crawler.indexing import faiss_store
from deep_crawler.crawler.extractor import simple_extract
from deep_crawler.llm.verifier import dangling_citations

# Load config from root directory
CFG = toml.load(Path(__file__).parent.parent / "config.toml")

def searx(q, n):
    r = requests.get(
        CFG["search"]["searx_url"],
        params={"q": q, "format": "json", "language": "en"},
        timeout=15,
    ).json()
    return [hit["url"] for hit in r.get("results", [])[:n]]

def main(question: str):
    print(f"🔍 Researching: {question}")

    print("🤖 AI Planner: Analyzing question and creating research strategy...")
    outline, kws, sections = plan_with_sections(question)
    print(f"📋 Research Plan: {len(kws)} keywords, {len(sections)} sections")
    print(f"🎯 Keywords: {', '.join(kws)}")
    
    print(f"\n📋 Research Outline:")
    for line in outline.splitlines():
        if line.strip() and line.startswith('#'):
            print(f"   {line}")
    print("")

    print(f"🔍 Searching for sources...")
    urls = []
    for i, kw in enumerate(kws, 1):
        print(f"   🔎 [{i}/{len(kws)}] Searching: '{kw}'")
        new_urls = searx(kw, CFG["search"]["urls_per_keyword"])
        urls += new_urls
        print(f"      ➡️ Found {len(new_urls)} URLs for '{kw}'")
    
    urls = list(dict.fromkeys(urls))  # dedupe
    print(f"🌐 Total unique URLs found: {len(urls)}")
    print(f"🕷️ Starting web crawling process...\n")

    # Enhanced crawling with individual URL feedback
    print(f"📄 Crawling websites:")
    for i, url in enumerate(urls, 1):
        print(f"   🌐 [{i}/{len(urls)}] Crawling: {url[:80]}{'...' if len(url) > 80 else ''}")
    
    pages = asyncio.run(crawl_urls(urls))
    if not pages:
        raise RuntimeError("No pages scraped.")

    print(f"\n✅ Crawling complete! Successfully processed {len(pages)} pages")
    print(f"❌ Failed to crawl {len(urls) - len(pages)} pages")
    
    # Increased text limit per page for more detailed content
    print(f"\n🔗 Building knowledge index...")
    texts = [p["markdown"][:8192] for p in pages]
    print(f"   📊 Processing {len(texts)} documents...")
    index = faiss_store.build(texts)
    print(f"   ✅ Search index built with {len(texts)} documents")

    # Create a more professional document structure
    doc = [f"# {question}", ""]
    
    print(f"\n✍️ Writing detailed report sections...")
    print(f"🤖 AI Writer: Generating {len(sections)} comprehensive sections\n")
    
    for i, sec in enumerate(sections, 1):
        print(f"📝 Section {i}/{len(sections)}: {sec}")
        print(f"   🤖 AI Analyzing: Searching knowledge base for '{sec}'...")
        print(f"   🔍 AI Processing: Finding relevant sources and information...")
        
        section_content = summarise_section(sec, index, texts)
        
        print(f"   ✅ AI Generated: {len(section_content)} characters of content")
        print(f"   📊 Section quality: {len(section_content.split())} words, {len(section_content.splitlines())} paragraphs")
        
        doc.append(f"## {sec}")
        doc.append(section_content)
        doc.append("")  # Add spacing between sections
        doc.append("")
        print("")  # Visual separation between sections

    print("📚 Adding references and citations...")
    doc.append("## References")
    doc.append("")
    print(f"   📑 Processing {len(pages)} source references...")
    for i, p in enumerate(pages, 1):
        title = p["title"] or "Untitled"
        ref = f"[{i}] **{title}** — {p['url']}"
        doc.append(ref)
        if i <= 5:  # Show first few references being added
            print(f"   📖 [{i}] {title[:50]}{'...' if len(title) > 50 else ''}")
    
    if len(pages) > 5:
        print(f"   📚 ... and {len(pages) - 5} more references")

    md = "\n".join(doc)
    
    print(f"\n🔍 AI Verifier: Checking for citation accuracy...")
    dangling = dangling_citations(md, set(range(1, len(pages) + 1)))
    if dangling:
        print(f"⚠️  Found {len(dangling)} dangling citations: {dangling}")
        print(f"   🔧 Citations that need review: {', '.join(map(str, dangling))}")
    else:
        print(f"   ✅ All citations are properly referenced")

    # Still save the file but also return the content
    out = Path(f"report_{hashlib.md5(question.encode()).hexdigest()[:8]}.md")
    out.write_text(md, encoding="utf-8")
    
    print(f"\n🎉 Research Complete!")
    print(f"📄 Report saved to: {out}")
    print(f"📊 Final Statistics:")
    print(f"   • Total characters: {len(md):,}")
    print(f"   • Report sections: {len(sections)}")
    print(f"   • Source documents: {len(pages)}")
    print(f"   • Keywords researched: {len(kws)}")
    print(f"   • URLs processed: {len(urls)}")
    print(f"   • Success rate: {len(pages)}/{len(urls)} ({len(pages)/len(urls)*100:.1f}%)")
    
    return md

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: cli.py \"research question\"")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))

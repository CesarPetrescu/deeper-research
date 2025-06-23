#!/usr/bin/env python3
"""
Enhanced CLI with LangChain/LangGraph integration.
Provides both traditional and advanced workflow options.
"""

import toml
import requests
import hashlib
import asyncio
import textwrap
from pathlib import Path
from tqdm import tqdm
from deep_crawler.crawler.firecrawl_async import crawl_urls
from deep_crawler.indexing import faiss_store
from deep_crawler.crawler.extractor import simple_extract
from deep_crawler.llm.verifier import dangling_citations

# Enhanced LLM imports
try:
    from deep_crawler.llm.enhanced_planner import plan_with_sections
    from deep_crawler.llm.enhanced_summariser import summarise_section, generate_research_insights
    # Skip LangGraph for now to avoid complexity
    # from deep_crawler.llm.langgraph_workflow import research_workflow
    LANGCHAIN_AVAILABLE = True
    LANGGRAPH_AVAILABLE = False
    print("🚀 LangChain Enhanced Mode: Available")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️ LangChain Enhanced Mode: Unavailable ({e})")
    # Fallback to traditional imports
    from deep_crawler.llm import planner, summariser

# Load config from root directory
CFG = toml.load(Path(__file__).parent.parent / "config.toml")

def searx(q, n):
    """Search using SearX with enhanced error handling."""
    try:
        r = requests.get(
            CFG["search"]["searx_url"],
            params={"q": q, "format": "json", "language": "en"},
            timeout=15,
        ).json()
        return [hit["url"] for hit in r.get("results", [])[:n]]
    except Exception as e:
        print(f"⚠️ Search error for '{q}': {e}")
        return []

def enhanced_main(question: str, use_langgraph: bool = False) -> str:
    """
    Enhanced main function with LangChain integration.
    
    Args:
        question: Research question
        use_langgraph: Whether to use the full LangGraph workflow (disabled for now)
        
    Returns:
        str: Generated research report
    """
    # Skip LangGraph for now
    if LANGCHAIN_AVAILABLE:
        return run_enhanced_traditional(question)
    else:
        return run_traditional_workflow(question)

def run_langgraph_workflow(question: str) -> str:
    """Run the full LangGraph workflow."""
    print(f"🚀 LangGraph Workflow: Starting advanced research orchestration")
    print(f"🔍 Research Question: {question}")
    
    try:
        # Use the LangGraph workflow
        report = research_workflow.run_research(question)
        
        # Save the report
        out = Path(f"report_{hashlib.md5(question.encode()).hexdigest()[:8]}.md")
        out.write_text(report, encoding="utf-8")
        
        print(f"🎉 LangGraph Research Complete!")
        print(f"📄 Report saved to: {out}")
        print(f"📊 Report length: {len(report):,} characters")
        
        return report
        
    except Exception as e:
        print(f"❌ LangGraph workflow failed: {e}")
        print(f"🔄 Falling back to enhanced traditional workflow...")
        return run_enhanced_traditional(question)

def run_enhanced_traditional(question: str) -> str:
    """Run enhanced traditional workflow with LangChain components."""
    print(f"🚀 Enhanced Traditional Workflow: LangChain-powered research")
    print(f"🔍 Researching: {question}")
    
    try:
        # Enhanced planning
        print(f"🤖 Enhanced AI Planner: Creating strategic research plan...")
        outline, keywords, sections = plan_with_sections(question)
        
        print(f"📋 Research Plan: {len(keywords)} keywords, {len(sections)} sections")
        print(f"🎯 Strategic Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
        
        # Enhanced outline display
        print(f"\n📋 Research Outline:")
        for line in outline.splitlines()[:8]:
            if line.strip() and line.startswith('#'):
                print(f"   {line}")
        if len(outline.splitlines()) > 8:
            print(f"   ... and more sections")
        print("")

        # Enhanced source searching
        print(f"🔍 Enhanced Source Discovery:")
        urls = []
        for i, kw in enumerate(keywords, 1):
            print(f"   🔎 [{i}/{len(keywords)}] Searching: '{kw}'")
            new_urls = searx(kw, CFG["search"]["urls_per_keyword"])
            urls += new_urls
            print(f"      ➡️ Found {len(new_urls)} URLs for '{kw}'")
        
        urls = list(dict.fromkeys(urls))  # dedupe
        print(f"🌐 Total unique URLs discovered: {len(urls)}")

        # Enhanced crawling
        print(f"🕷️ Enhanced Web Crawling:")
        for i, url in enumerate(urls[:10], 1):  # Show first 10 URLs
            print(f"   🌐 [{i}/{len(urls)}] {url[:80]}{'...' if len(url) > 80 else ''}")
        
        if len(urls) > 10:
            print(f"   🌐 ... and {len(urls) - 10} more URLs")
        
        pages = asyncio.run(crawl_urls(urls))
        if not pages:
            raise RuntimeError("No pages scraped.")

        print(f"\n✅ Crawling Results:")
        print(f"   📄 Successfully crawled: {len(pages)} pages")
        print(f"   ❌ Failed to crawl: {len(urls) - len(pages)} pages")
        print(f"   📊 Success rate: {len(pages)/len(urls)*100:.1f}%")
        
        # Enhanced indexing
        print(f"\n🔗 Enhanced Knowledge Processing:")
        texts = [p["markdown"][:8192] for p in pages]
        print(f"   📊 Processing {len(texts)} documents...")
        print(f"   🧠 Building semantic search index...")
        index = faiss_store.build(texts)
        print(f"   ✅ Knowledge base built with {len(texts)} documents")

        # Enhanced content generation
        print(f"\n✍️ Enhanced AI Content Generation:")
        doc = [f"# {question}", ""]
        
        for i, sec in enumerate(sections, 1):
            print(f"\n📝 Section {i}/{len(sections)}: {sec}")
            
            # Use enhanced summarizer
            section_content = summarise_section(sec, index, texts)
            
            doc.append(f"## {sec}")
            doc.append(section_content)
            doc.append("")
            doc.append("")

        # Generate enhanced insights
        if len(sections) > 1:
            print(f"\n🧠 Generating Research Insights...")
            all_content = [doc[i] for i in range(len(doc)) if doc[i].strip() and not doc[i].startswith('#')]
            insights = generate_research_insights(question, all_content[:5])  # Limit for token management
            
            if insights and len(insights) > 100:
                doc.append("## Key Insights and Analysis")
                doc.append(insights)
                doc.append("")
                doc.append("")

        # Enhanced references
        print(f"\n📚 Enhanced Reference Processing:")
        doc.append("## References")
        doc.append("")
        print(f"   📑 Processing {len(pages)} source references...")
        
        for i, p in enumerate(pages, 1):
            title = p["title"] or "Untitled"
            ref = f"[{i}] **{title}** — {p['url']}"
            doc.append(ref)
            
            if i <= 5:
                print(f"   📖 [{i}] {title[:50]}{'...' if len(title) > 50 else ''}")
        
        if len(pages) > 5:
            print(f"   📚 ... and {len(pages) - 5} more references")

        md = "\n".join(doc)
        
        # Enhanced verification
        print(f"\n🔍 Enhanced Quality Verification:")
        dangling = dangling_citations(md, set(range(1, len(pages) + 1)))
        if dangling:
            print(f"⚠️ Citation Issues: {len(dangling)} dangling citations found")
            print(f"   🔧 Citations needing review: {', '.join(map(str, dangling))}")
        else:
            print(f"   ✅ All citations properly referenced")

        # Save and report
        out = Path(f"report_{hashlib.md5(question.encode()).hexdigest()[:8]}.md")
        out.write_text(md, encoding="utf-8")
        
        print(f"\n🎉 Enhanced Research Complete!")
        print(f"📄 Report saved to: {out}")
        print(f"📊 Enhanced Statistics:")
        print(f"   • Total characters: {len(md):,}")
        print(f"   • Sections generated: {len(sections)}")
        print(f"   • Sources analyzed: {len(pages)}")
        print(f"   • Keywords researched: {len(keywords)}")
        print(f"   • URLs processed: {len(urls)}")
        print(f"   • Success rate: {len(pages)}/{len(urls)} ({len(pages)/len(urls)*100:.1f}%)")
        
        return md
        
    except Exception as e:
        print(f"❌ Enhanced workflow failed: {e}")
        print(f"🔄 Falling back to traditional workflow...")
        return run_traditional_workflow(question)

def run_traditional_workflow(question: str) -> str:
    """Fallback to traditional workflow."""
    print(f"🔄 Traditional Workflow: Basic research mode")
    print(f"🔍 Researching: {question}")
    
    # Use original planner and summariser
    outline, kws = planner.plan(question)
    print(f"📋 Research Plan: {len(kws)} keywords, {len([l for l in outline.splitlines() if l.startswith('##')])} sections")
    print("🔍 Keywords:", ", ".join(kws))

    urls = []
    for kw in kws:
        urls += searx(kw, CFG["search"]["urls_per_keyword"])
    urls = list(dict.fromkeys(urls))
    print(f"🌐 Found {len(urls)} unique URLs to research")

    pages = asyncio.run(crawl_urls(urls))
    if not pages:
        raise RuntimeError("No pages scraped.")

    print(f"📄 Successfully crawled {len(pages)} pages")
    
    texts = [p["markdown"][:8192] for p in pages]
    index = faiss_store.build(texts)
    print(f"🔗 Built search index with {len(texts)} documents")

    doc = [f"# {question}", ""]
    
    sections = []
    for line in outline.splitlines():
        if line.startswith("## "):
            section_title = line.strip("# ").strip()
            sections.append(section_title)
    
    print(f"✍️ Writing {len(sections)} sections...")
    
    for i, sec in enumerate(sections, 1):
        print(f"📝 Section {i}/{len(sections)}: {sec}")
        section_content = summariser.summarise_section(sec, index, texts)
        print(f"   ✅ Generated {len(section_content)} characters")
        
        doc.append(f"## {sec}")
        doc.append(section_content)
        doc.append("")
        doc.append("")

    print("📚 Adding references...")
    doc.append("## References")
    doc.append("")
    for i, p in enumerate(pages, 1):
        title = p["title"] or "Untitled"
        ref = f"[{i}] **{title}** — {p['url']}"
        doc.append(ref)

    md = "\n".join(doc)
    dangling = dangling_citations(md, set(range(1, len(pages) + 1)))
    if dangling:
        print(f"⚠️ Found {len(dangling)} dangling citations: {dangling}")

    out = Path(f"report_{hashlib.md5(question.encode()).hexdigest()[:8]}.md")
    out.write_text(md, encoding="utf-8")
    print(f"✅ Complete! Report saved to {out}")
    print(f"📊 Final report: {len(md)} characters, {len(sections)} sections, {len(pages)} sources")
    
    return md

def main(question: str) -> str:
    """
    Main research function with automatic workflow selection.
    
    Args:
        question: The research question
        
    Returns:
        str: Generated research report
    """
    # Check if we should use advanced workflows
    use_langgraph = CFG.get("llm", {}).get("use_langgraph", False)
    
    if LANGCHAIN_AVAILABLE:
        print(f"🚀 LangChain Enhanced Mode: Active")
        if use_langgraph:
            print(f"🔬 Using LangGraph advanced workflow orchestration")
        else:
            print(f"🔧 Using LangChain enhanced traditional workflow")
    else:
        print(f"🔄 Traditional Mode: LangChain not available")
    
    return enhanced_main(question, use_langgraph=use_langgraph)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: enhanced_cli.py \"research question\"")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))

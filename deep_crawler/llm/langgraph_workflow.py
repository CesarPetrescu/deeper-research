#!/usr/bin/env python3
"""
LangGraph Research Workflow Orchestrator
Advanced workflow management for the research process using state machines.
"""

import asyncio
import hashlib
import numpy as np
import faiss
from typing import Dict, List, Any, TypedDict
from pathlib import Path
import toml

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .enhanced_core import research_planner, content_synthesizer, quality_verifier
from ..indexing import faiss_store
from ..indexing.embed_cache import get_vector
from ..crawler.firecrawl_async import crawl_urls

# Load configuration
CONFIG = toml.load(Path(__file__).parent.parent.parent / "config.toml")

class ResearchState(TypedDict):
    """State object for the research workflow."""
    question: str
    research_plan: Dict[str, Any]
    keywords: List[str]
    urls: List[str]
    crawled_pages: List[Dict[str, Any]]
    knowledge_index: Any
    sections: List[str]
    generated_content: Dict[str, str]
    quality_scores: Dict[str, float]
    final_report: str
    errors: List[str]
    progress: float

class ResearchWorkflow:
    """
    Advanced research workflow using LangGraph state machine.
    """
    
    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._build_workflow_graph()
        
    def _build_workflow_graph(self) -> StateGraph:
        """Build the research workflow state graph."""
        
        # Create the state graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes for each step
        workflow.add_node("plan_research", self.plan_research_node)
        workflow.add_node("search_sources", self.search_sources_node)
        workflow.add_node("crawl_content", self.crawl_content_node)
        workflow.add_node("build_index", self.build_index_node)
        workflow.add_node("generate_sections", self.generate_sections_node)
        workflow.add_node("quality_check", self.quality_check_node)
        workflow.add_node("finalize_report", self.finalize_report_node)
        workflow.add_node("handle_errors", self.handle_errors_node)
        
        # Set entry point
        workflow.set_entry_point("plan_research")
        
        # Add edges (workflow transitions)
        workflow.add_edge("plan_research", "search_sources")
        workflow.add_edge("search_sources", "crawl_content")
        workflow.add_edge("crawl_content", "build_index")
        workflow.add_edge("build_index", "generate_sections")
        workflow.add_edge("generate_sections", "quality_check")
        
        # Conditional edges based on quality
        workflow.add_conditional_edges(
            "quality_check",
            self.quality_decision,
            {
                "finalize": "finalize_report",
                "retry": "generate_sections",
                "error": "handle_errors"
            }
        )
        
        workflow.add_edge("finalize_report", END)
        workflow.add_edge("handle_errors", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def plan_research_node(self, state: ResearchState) -> ResearchState:
        """Research planning node."""
        print(f"🧠 Workflow Node: Research Planning")
        
        try:
            question = state["question"]
            outline, keywords, approach = research_planner.create_research_strategy(question)
            
            # Ensure outline is a string
            if isinstance(outline, dict):
                outline = str(outline)
            elif not isinstance(outline, str):
                outline = ""
            
            # Extract sections from outline
            sections = []
            try:
                for line in outline.splitlines():
                    if line.startswith("## "):
                        sections.append(line.strip("# ").strip())
            except AttributeError:
                # If outline doesn't have splitlines method, skip section extraction
                pass
            
            state["research_plan"] = {
                "outline": outline,
                "approach": approach,
                "sections": sections
            }
            state["keywords"] = keywords
            state["sections"] = sections
            state["progress"] = 10.0
            
            print(f"✅ Planning Complete: {len(keywords)} keywords, {len(sections)} sections")
            
        except Exception as e:
            state["errors"].append(f"Planning error: {str(e)}")
            print(f"❌ Planning Error: {e}")
        
        return state
    
    def search_sources_node(self, state: ResearchState) -> ResearchState:
        """Source searching node."""
        print(f"🔍 Workflow Node: Source Searching")
        
        try:
            import requests
            
            urls = []
            keywords = state["keywords"]
            
            for i, kw in enumerate(keywords):
                print(f"   🔎 [{i+1}/{len(keywords)}] Searching: '{kw}'")
                
                # Use SearX for searching
                try:
                    r = requests.get(
                        CONFIG["search"]["searx_url"],
                        params={"q": kw, "format": "json", "language": "en"},
                        timeout=15,
                    ).json()
                    
                    new_urls = [hit["url"] for hit in r.get("results", [])[:CONFIG["search"]["urls_per_keyword"]]]
                    urls.extend(new_urls)
                    print(f"      ➡️ Found {len(new_urls)} URLs for '{kw}'")
                    
                except Exception as e:
                    print(f"      ⚠️ Search error for '{kw}': {e}")
            
            # Remove duplicates
            urls = list(dict.fromkeys(urls))
            state["urls"] = urls
            state["progress"] = 25.0
            
            print(f"✅ Search Complete: {len(urls)} unique URLs found")
            
        except Exception as e:
            state["errors"].append(f"Search error: {str(e)}")
            print(f"❌ Search Error: {e}")
        
        return state
    
    def crawl_content_node(self, state: ResearchState) -> ResearchState:
        """Content crawling node."""
        print(f"🕷️ Workflow Node: Content Crawling")
        
        try:
            urls = state["urls"]
            print(f"📄 Crawling {len(urls)} websites...")
            
            # Crawl URLs asynchronously
            pages = asyncio.run(crawl_urls(urls))
            
            state["crawled_pages"] = pages
            state["progress"] = 50.0
            
            print(f"✅ Crawling Complete: {len(pages)} pages successfully processed")
            print(f"❌ Failed: {len(urls) - len(pages)} pages could not be crawled")
            
        except Exception as e:
            state["errors"].append(f"Crawling error: {str(e)}")
            print(f"❌ Crawling Error: {e}")
        
        return state
    
    def build_index_node(self, state: ResearchState) -> ResearchState:
        """Knowledge index building node."""
        print(f"🔗 Workflow Node: Building Knowledge Index")
        
        try:
            pages = state["crawled_pages"]
            
            if not pages:
                raise RuntimeError("No pages available for indexing")
            
            # Extract text content
            texts = [p["markdown"][:8192] for p in pages]
            
            # Build search index
            print(f"   📊 Processing {len(texts)} documents...")
            index = faiss_store.build(texts)
            
            state["knowledge_index"] = index
            state["progress"] = 60.0
            
            print(f"✅ Index Built: {len(texts)} documents indexed")
            
        except Exception as e:
            state["errors"].append(f"Indexing error: {str(e)}")
            print(f"❌ Indexing Error: {e}")
        
        return state
    
    def generate_sections_node(self, state: ResearchState) -> ResearchState:
        """Content generation node."""
        print(f"✍️ Workflow Node: Content Generation")
        
        try:
            sections = state["sections"]
            index = state["knowledge_index"]
            pages = state["crawled_pages"]
            texts = [p["markdown"][:8192] for p in pages]
            
            generated_content = {}
            
            for i, section in enumerate(sections):
                print(f"📝 Generating Section {i+1}/{len(sections)}: {section}")
                
                # Use enhanced content synthesizer
                content = content_synthesizer.synthesize_section(
                    section_title=section,
                    relevant_docs=self._get_relevant_docs(section, index, texts),
                    full_texts=texts
                )
                
                generated_content[section] = content
                
                # Update progress
                section_progress = 60 + (i + 1) / len(sections) * 25
                state["progress"] = section_progress
            
            state["generated_content"] = generated_content
            state["progress"] = 85.0
            
            print(f"✅ Content Generation Complete: {len(sections)} sections written")
            
        except Exception as e:
            state["errors"].append(f"Generation error: {str(e)}")
            print(f"❌ Generation Error: {e}")
        
        return state
    
    def quality_check_node(self, state: ResearchState) -> ResearchState:
        """Quality verification node."""
        print(f"🔍 Workflow Node: Quality Verification")
        
        try:
            generated_content = state["generated_content"]
            question = state["question"]
            pages = state["crawled_pages"]
            
            quality_scores = {}
            overall_quality = 0
            
            for section, content in generated_content.items():
                print(f"   🔍 Checking quality of: {section}")
                
                # Verify section quality
                quality_result = quality_verifier.verify_research_quality(
                    content=content,
                    question=f"{question} - {section}",
                    source_count=len(pages)
                )
                
                quality_score = quality_result.get("quality_score", 7)
                quality_scores[section] = quality_score
                overall_quality += quality_score
                
                print(f"   📊 {section}: {quality_score}/10")
            
            overall_quality /= len(generated_content)
            state["quality_scores"] = quality_scores
            state["progress"] = 90.0
            
            print(f"✅ Quality Check Complete: Overall score {overall_quality:.1f}/10")
            
        except Exception as e:
            state["errors"].append(f"Quality check error: {str(e)}")
            print(f"❌ Quality Check Error: {e}")
        
        return state
    
    def quality_decision(self, state: ResearchState) -> str:
        """Decide next step based on quality scores."""
        if state.get("errors"):
            return "error"
        
        quality_scores = state.get("quality_scores", {})
        if not quality_scores:
            return "error"
        
        avg_quality = sum(quality_scores.values()) / len(quality_scores)
        
        if avg_quality >= 7.0:
            return "finalize"
        elif avg_quality >= 5.0:
            return "finalize"  # Accept moderate quality
        else:
            return "retry"  # Quality too low, retry generation
    
    def finalize_report_node(self, state: ResearchState) -> ResearchState:
        """Report finalization node."""
        print(f"📄 Workflow Node: Report Finalization")
        
        try:
            question = state["question"]
            research_plan = state["research_plan"]
            generated_content = state["generated_content"]
            pages = state["crawled_pages"]
            
            # Build final report
            report_parts = [f"# {question}", ""]
            
            # Add sections
            for section, content in generated_content.items():
                report_parts.append(f"## {section}")
                report_parts.append(content)
                report_parts.append("")
            
            # Add references
            report_parts.append("## References")
            report_parts.append("")
            for i, page in enumerate(pages, 1):
                title = page.get("title", "Untitled")
                url = page.get("url", "")
                report_parts.append(f"[{i}] **{title}** — {url}")
            
            final_report = "\n".join(report_parts)
            state["final_report"] = final_report
            state["progress"] = 100.0
            
            print(f"✅ Report Finalized: {len(final_report)} characters")
            
        except Exception as e:
            state["errors"].append(f"Finalization error: {str(e)}")
            print(f"❌ Finalization Error: {e}")
        
        return state
    
    def handle_errors_node(self, state: ResearchState) -> ResearchState:
        """Error handling node."""
        print(f"⚠️ Workflow Node: Error Handling")
        
        errors = state.get("errors", [])
        if errors:
            print(f"❌ Workflow completed with {len(errors)} errors:")
            for error in errors:
                print(f"   • {error}")
        
        # Generate basic report even with errors
        if not state.get("final_report"):
            state["final_report"] = f"# {state['question']}\n\nResearch could not be completed due to errors."
        
        return state
    
    def _get_relevant_docs(self, section: str, index: Any, texts: List[str]) -> List[str]:
        """Get relevant documents for a section using the search index."""
        try:
            # Convert section title to vector for FAISS search
            query_vector = get_vector(section)
            query_vector = np.array([query_vector], dtype="float32")
            faiss.normalize_L2(query_vector)
            
            # Search the index
            _, relevant_indices = index.search(query_vector, k=min(5, len(texts)))
            relevant_doc_indices = relevant_indices[0]  # Extract indices from search results
            
            relevant_docs = []
            for idx in relevant_doc_indices:
                if 0 <= idx < len(texts):
                    relevant_docs.append(texts[idx])
            
            return relevant_docs
        except Exception:
            # Fallback to first few texts
            return texts[:3]
    
    def run_research(self, question: str) -> str:
        """
        Run the complete research workflow.
        
        Args:
            question: The research question
            
        Returns:
            str: The final research report
        """
        print(f"🚀 LangGraph Workflow: Starting enhanced research process")
        
        # Initialize state
        initial_state = ResearchState(
            question=question,
            research_plan={},
            keywords=[],
            urls=[],
            crawled_pages=[],
            knowledge_index=None,
            sections=[],
            generated_content={},
            quality_scores={},
            final_report="",
            errors=[],
            progress=0.0
        )
        
        # Generate a unique thread ID
        thread_id = hashlib.md5(question.encode()).hexdigest()[:8]
        
        # Run the workflow
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Execute the workflow
            result = self.graph.invoke(initial_state, config)
            
            final_report = result.get("final_report", "")
            errors = result.get("errors", [])
            
            if errors:
                print(f"⚠️ Workflow completed with warnings: {len(errors)} issues")
            else:
                print(f"🎉 Workflow completed successfully!")
            
            return final_report
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return f"# {question}\n\nResearch workflow failed: {str(e)}"

# Global workflow instance
research_workflow = ResearchWorkflow()

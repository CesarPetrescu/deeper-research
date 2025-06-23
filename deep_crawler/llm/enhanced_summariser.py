#!/usr/bin/env python3
"""
Enhanced Content Summarizer using LangChain for intelligent content synthesis.
"""

import toml
import numpy as np
import faiss
from pathlib import Path
from typing import List, Any
from .enhanced_core import content_synthesizer, quality_verifier
from ..indexing.embed_cache import get_vector

# Load configuration
CONFIG = toml.load(Path(__file__).parent.parent.parent / "config.toml")

def summarise_section(section_title: str, index: Any, texts: List[str]) -> str:
    """
    Generate a comprehensive section using advanced LangChain-based content synthesis.
    
    Args:
        section_title: The title of the section to generate
        index: The FAISS search index for finding relevant content
        texts: List of all source texts
        
    Returns:
        str: Synthesized section content
    """
    print(f"🧠 AI Content Synthesizer: Starting analysis for '{section_title}'")
    
    # Search for relevant content using the existing FAISS index
    print(f"🔍 AI Searching: Finding relevant sources in knowledge base...")
    
    try:
        # Query the index for relevant documents using proper vector search
        # Convert section title to vector for FAISS search
        query_vector = get_vector(section_title)
        query_vector = np.array([query_vector], dtype="float32")
        faiss.normalize_L2(query_vector)
        
        # Search the index
        _, relevant_indices = index.search(query_vector, k=min(8, len(texts)))
        relevant_doc_indices = relevant_indices[0]  # Extract indices from search results
        
        # Extract the actual text content from search results
        relevant_texts = []
        for doc_idx in relevant_doc_indices:
            if 0 <= doc_idx < len(texts):
                relevant_texts.append(texts[doc_idx])
        
        print(f"📊 Found {len(relevant_texts)} relevant sources for '{section_title}'")
        
        # Use the enhanced content synthesizer
        synthesized_content = content_synthesizer.synthesize_section(
            section_title=section_title,
            relevant_docs=relevant_texts,
            full_texts=texts
        )
        
        # Perform quality verification
        print(f"🔍 AI Quality Check: Verifying content accuracy and completeness...")
        quality_results = quality_verifier.verify_research_quality(
            content=synthesized_content,
            question=section_title,
            source_count=len(relevant_texts)
        )
        
        # Log quality results
        quality_score = quality_results.get("quality_score", 7)
        issues = quality_results.get("issues", [])
        
        print(f"📊 Content Quality Score: {quality_score}/10")
        if issues:
            print(f"⚠️ Quality Issues: {len(issues)} concerns identified")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"   • {issue}")
        else:
            print(f"✅ Quality Check: No significant issues found")
        
        # If quality is low, attempt improvement
        if quality_score < 6 and len(relevant_texts) > 3:
            print(f"🔄 Low quality detected, attempting content improvement...")
            synthesized_content = _improve_content_quality(
                synthesized_content, section_title, relevant_texts[:5]
            )
        
        print(f"✅ Section Complete: {len(synthesized_content)} characters generated")
        
        return synthesized_content
        
    except Exception as e:
        print(f"⚠️ Enhanced synthesis error: {e}")
        print(f"🔧 Error type: {type(e).__name__}")
        print(f"🔧 Section title: {section_title}")
        print(f"🔧 Number of relevant texts: {len(relevant_texts) if 'relevant_texts' in locals() else 'unknown'}")
        print(f"🔧 Index type: {type(index)}")
        
        # Try direct synthesis as backup
        print(f"🔄 Attempting direct LLM synthesis...")
        try:
            from .direct_synthesis import synthesise_section_direct
            result = synthesise_section_direct(section_title, index, texts)
            print(f"✅ Direct synthesis successful: {len(result)} characters")
            return result
        except Exception as direct_error:
            print(f"⚠️ Direct synthesis also failed: {direct_error}")
            return _fallback_summarization(section_title, texts)

def _improve_content_quality(content: str, section_title: str, sources: List[str]) -> str:
    """
    Attempt to improve content quality by re-synthesizing with better prompts.
    """
    try:
        print(f"🔧 AI Enhancement: Re-generating content with quality improvements...")
        
        # Use a more focused synthesis approach
        improved_content = content_synthesizer.synthesize_section(
            section_title=f"Enhanced analysis: {section_title}",
            relevant_docs=sources,
            full_texts=sources
        )
        
        if len(improved_content) > len(content):
            print(f"✅ Quality Improved: Generated {len(improved_content) - len(content)} additional characters")
            return improved_content
        else:
            return content
            
    except Exception as e:
        print(f"⚠️ Content improvement failed: {e}")
        return content

def _fallback_summarization(section_title: str, texts: List[str]) -> str:
    """
    Fallback method for content generation if LangChain fails.
    """
    print(f"🔄 Using fallback summarization for '{section_title}'...")
    
    if not texts:
        return f"No content available for {section_title}."
    
    # Simple keyword-based filtering and summarization
    relevant_texts = []
    keywords = section_title.lower().split()
    
    for text in texts[:10]:  # Limit to first 10 texts
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in keywords):
            relevant_texts.append(text[:800])  # Limit text length
    
    if not relevant_texts:
        relevant_texts = texts[:3]  # Use first 3 texts as fallback
    
    # Create basic summary
    summary = f"Based on available sources:\n\n"
    for i, text in enumerate(relevant_texts[:3]):
        summary += f"{text[:400]}...\n\n"
    
    return summary

def generate_research_insights(question: str, all_sections: List[str]) -> str:
    """
    Generate overall research insights using advanced AI analysis.
    
    Args:
        question: The original research question
        all_sections: List of all generated section content
        
    Returns:
        str: Generated insights and analysis
    """
    print(f"🧠 AI Insight Generator: Creating comprehensive research insights...")
    
    try:
        # Combine all sections for analysis
        combined_content = "\n\n".join(all_sections)
        
        # Use the content synthesizer for high-level insights
        insights = content_synthesizer.synthesize_section(
            section_title="Research Insights and Key Findings",
            relevant_docs=[combined_content[:3000]],  # Limit for token management
            full_texts=all_sections
        )
        
        print(f"✅ Research Insights: {len(insights)} characters of analysis generated")
        
        return insights
        
    except Exception as e:
        print(f"⚠️ Insights generation error: {e}")
        return "Key insights could not be generated automatically."

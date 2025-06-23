#!/usr/bin/env python3
"""
Direct LLM synthesis without LangChain for reliable content generation.
"""

import toml
from pathlib import Path
from typing import List
from deep_crawler.llm.core import chat

# Load configuration
CONFIG = toml.load(Path(__file__).parent.parent.parent / "config.toml")

def synthesize_content_direct(section_title: str, relevant_docs: List[str]) -> str:
    """
    Direct LLM synthesis without LangChain complexity.
    """
    print(f"🧠 Direct LLM Synthesis: Processing '{section_title}'...")
    
    # Prepare content for synthesis
    sources_text = ""
    for i, doc in enumerate(relevant_docs[:3]):  # Limit to 3 sources
        source_content = doc[:600] if len(doc) > 600 else doc  # Limit each source
        sources_text += f"[{i+1}] {source_content}\n\n"
    
    # Create focused prompt
    system_prompt = """You are an expert research writer. Create a comprehensive, well-written section that synthesizes information from the provided sources. Write in a professional, informative style with clear structure. Use citations [1], [2], etc. to reference the sources. Aim for 300-500 words."""
    
    user_prompt = f"""Write a detailed section about: {section_title}

Sources:
{sources_text}

Create a well-structured, informative section that synthesizes the key information from these sources. Use proper citations and provide insights."""
    
    try:
        # Use direct chat function
        result = chat(system_prompt, user_prompt, max_tokens=800)
        print(f"✅ Direct Synthesis: Generated {len(result)} characters")
        return result
        
    except Exception as e:
        print(f"⚠️ Direct synthesis failed: {e}")
        # Simple fallback
        return f"## {section_title}\n\nBased on the available sources:\n\n{sources_text[:1000]}..."

def synthesise_section_direct(section_title: str, index, texts: List[str]) -> str:
    """
    Direct replacement for enhanced_summariser.summarise_section that actually works.
    """
    print(f"🔍 Direct Section Synthesis: '{section_title}'")
    
    # Simple relevance search - find texts containing keywords from section title
    keywords = section_title.lower().replace("and", "").replace("or", "").split()
    relevant_texts = []
    
    for text in texts:
        text_lower = text.lower()
        relevance_score = sum(1 for keyword in keywords if keyword in text_lower)
        if relevance_score > 0:
            relevant_texts.append((relevance_score, text))
    
    # Sort by relevance and take top 5
    relevant_texts.sort(key=lambda x: x[0], reverse=True)
    selected_texts = [text for score, text in relevant_texts[:5]]
    
    if not selected_texts:
        selected_texts = texts[:3]  # Fallback to first 3 texts
    
    print(f"📊 Found {len(selected_texts)} relevant sources")
    
    # Use direct synthesis
    return synthesize_content_direct(section_title, selected_texts)

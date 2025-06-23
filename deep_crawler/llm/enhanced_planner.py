#!/usr/bin/env python3
"""
Enhanced Research Planner using LangChain for strategic research planning.
"""

import toml
from pathlib import Path
from typing import List, Tuple
from .enhanced_core import research_planner

# Load configuration
CONFIG = toml.load(Path(__file__).parent.parent.parent / "config.toml")

def plan(question: str) -> Tuple[str, List[str]]:
    """
    Create a comprehensive research plan using advanced LangChain-based AI planning.
    
    Args:
        question: The research question to plan for
        
    Returns:
        tuple: (research_outline, strategic_keywords)
    """
    print(f"🤖 Enhanced AI Planner: Initializing strategic research planning...")
    
    # Use the enhanced research planner
    outline, keywords, approach = research_planner.create_research_strategy(question)
    
    # Ensure outline is a string for safe processing
    if isinstance(outline, dict):
        outline = str(outline)
    elif not isinstance(outline, str):
        outline = ""
    
    # Log the planning results with enhanced feedback
    print(f"📋 Strategic Outline Generated:")
    try:
        outline_lines = outline.splitlines() if outline else []
        for i, line in enumerate(outline_lines[:5]):  # Show first 5 lines
            if line.strip():
                print(f"   {line}")
        
        if len(outline_lines) > 5:
            print(f"   ... and {len(outline_lines) - 5} more outline items")
    except AttributeError:
        print(f"   {outline}")
    
    print(f"🎯 Strategic Keywords ({len(keywords)}):")
    for i, kw in enumerate(keywords[:8]):  # Show first 8 keywords
        print(f"   {i+1}. {kw}")
    
    if len(keywords) > 8:
        print(f"   ... and {len(keywords) - 8} more keywords")
    
    print(f"📊 Research Strategy: {approach[:100]}...")
    
    return outline, keywords

def extract_sections_from_outline(outline: str) -> List[str]:
    """
    Extract section titles from the research outline.
    
    Args:
        outline: The research outline text
        
    Returns:
        List of section titles
    """
    sections = []
    
    # Ensure outline is a string
    if isinstance(outline, dict):
        outline = str(outline)
    elif not isinstance(outline, str):
        outline = ""
    
    try:
        for line in outline.splitlines():
            if line.startswith("## "):
                section_title = line.strip("# ").strip()
                sections.append(section_title)
    except AttributeError:
        # If outline still doesn't have splitlines method, return empty list
        pass
    
    return sections

def plan_with_sections(question: str) -> Tuple[str, List[str], List[str]]:
    """
    Enhanced planning that returns outline, keywords, and extracted sections.
    
    Args:
        question: The research question
        
    Returns:
        tuple: (outline, keywords, section_titles)
    """
    outline, keywords = plan(question)
    sections = extract_sections_from_outline(outline)
    
    print(f"📝 Extracted {len(sections)} research sections for content generation")
    
    return outline, keywords, sections

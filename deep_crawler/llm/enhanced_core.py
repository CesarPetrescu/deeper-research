#!/usr/bin/env python3
"""
Enhanced LLM Core using LangChain for sophisticated AI orchestration.
This module provides advanced AI capabilities with memory, context management,
and intelligent workflow orchestration.
"""

import os
import toml
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage
from .custom_llm import CustomOpenAILLM
import json

# Load configuration
CONFIG = toml.load(Path(__file__).parent.parent.parent / "config.toml")

class EnhancedLLMCore:
    """
    Advanced LLM orchestration using LangChain for intelligent research workflows.
    """
    
    def __init__(self):
        self.llm = CustomOpenAILLM()
        
        # Initialize memory for context preservation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Research state to maintain context across the workflow
        self.research_state = {}
        
    def update_research_state(self, key: str, value: Any):
        """Update research state for context preservation."""
        self.research_state[key] = value
        print(f"🧠 Context Updated: {key} -> {type(value).__name__}")
    
    def get_research_context(self) -> str:
        """Get formatted research context for prompts."""
        if not self.research_state:
            return "No previous research context."
        
        context_items = []
        for key, value in self.research_state.items():
            if isinstance(value, (list, dict)):
                context_items.append(f"{key}: {len(value)} items")
            else:
                context_items.append(f"{key}: {str(value)[:100]}...")
        
        return "Current research context:\n" + "\n".join(context_items)

class ResearchPlanner(EnhancedLLMCore):
    """
    Advanced research planning using LangChain chains for strategic thinking.
    """
    
    def __init__(self):
        super().__init__()
        
        # Strategic planning prompt template
        self.planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert research strategist. Your job is to analyze research questions 
            and create comprehensive, strategic research plans.
            
            For any research question, you should:
            1. Analyze the question depth and complexity
            2. Identify key research dimensions and angles
            3. Generate targeted keywords for comprehensive coverage
            4. Create a logical outline structure
            5. Consider potential challenges and information gaps
            
            Always provide structured, actionable research strategies."""),
            
            ("human", """Research Question: {question}
            
            {context}
            
            Create a comprehensive research strategy with:
            1. Research outline (sections as ## headers)
            2. Strategic keywords (8-12 high-value terms)
            3. Research approach recommendations
            
            You MUST respond with valid JSON in this exact format:
            {{
                "outline": "# Topic Title\\n\\n## Section 1\\nDescription...\\n\\n## Section 2\\nDescription...",
                "keywords": ["keyword1", "keyword2", "keyword3"],
                "approach": "Description of research approach methodology"
            }}
            
            Ensure the outline is a string with newlines (\\n) separating sections, keywords is a list of strings, and approach is a string.""")
        ])
        
        # Create the planning chain
        self.planning_chain = (
            self.planning_prompt 
            | self.llm 
            | JsonOutputParser()
        )
        
    def create_research_strategy(self, question: str) -> tuple[str, List[str], str]:
        """
        Create a comprehensive research strategy using advanced AI planning.
        
        Returns:
            tuple: (outline, keywords, approach_description)
        """
        print(f"🧠 AI Strategic Planner: Analyzing research question complexity...")
        
        # Get current research context
        context = self.get_research_context()
        
        try:
            # Execute the planning chain
            result = self.planning_chain.invoke({
                "question": question,
                "context": context
            })
            
            # Validate the result structure
            if not isinstance(result, dict):
                raise ValueError(f"Expected dict result, got {type(result)}")
            
            outline = result.get("outline", "")
            keywords = result.get("keywords", [])
            approach = result.get("approach", "Standard research approach")
            
            # Ensure outline is a string (handle case where JSON parsing returns dict)
            if isinstance(outline, dict):
                print(f"⚠️ Warning: Outline returned as dict, converting to string")
                outline = str(outline)
            elif not isinstance(outline, str):
                print(f"⚠️ Warning: Outline is not a string, type: {type(outline)}")
                outline = ""
            
            # Ensure keywords is a list
            if not isinstance(keywords, list):
                print(f"⚠️ Warning: Keywords is not a list, type: {type(keywords)}")
                keywords = []
            
            # Ensure approach is a string
            if not isinstance(approach, str):
                print(f"⚠️ Warning: Approach is not a string, type: {type(approach)}")
                approach = "Standard research approach"
            
            # Update research state
            self.update_research_state("research_question", question)
            self.update_research_state("research_outline", outline)
            self.update_research_state("keywords", keywords)
            self.update_research_state("approach", approach)
            
            # Count sections safely
            section_count = outline.count('##') if isinstance(outline, str) else 0
            print(f"🎯 Strategy Created: {len(keywords)} keywords, {section_count} sections")
            print(f"📋 Research Approach: {approach[:100]}...")
            
            return outline, keywords, approach
            
        except Exception as e:
            print(f"⚠️ Planning error: {e}")
            print(f"🔄 Error details: {type(e).__name__} - {str(e)}")
            # Fallback to basic planning
            return self._fallback_planning(question)
    
    def _fallback_planning(self, question: str) -> tuple[str, List[str], str]:
        """Fallback planning method if LangChain fails."""
        print("🔄 Using fallback planning method...")
        
        basic_outline = f"""# {question}

## Introduction
## Main Analysis  
## Key Findings
## Conclusion"""
        
        basic_keywords = [
            question.replace("?", "").replace(".", ""),
            "overview", "analysis", "current trends", "expert opinion"
        ]
        
        return basic_outline, basic_keywords, "Basic research approach"

class ContentSynthesizer(EnhancedLLMCore):
    """
    Advanced content synthesis using LangChain for intelligent content generation.
    """
    
    def __init__(self):
        super().__init__()
        
        # Content synthesis prompt template
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert content synthesizer and research writer. Your job is to 
            analyze multiple sources and create coherent, comprehensive content sections.
            
            Key principles:
            1. Synthesize information from multiple sources, don't just summarize
            2. Identify patterns, connections, and insights across sources
            3. Maintain objectivity while being engaging
            4. Use specific details and evidence
            5. Ensure logical flow and clear structure
            6. Cite sources appropriately with [1], [2], etc.
            
            Write in a professional, informative style suitable for research reports."""),
            
            ("human", """Section Topic: {section_title}
            
            Research Context:
            {research_context}
            
            Available Sources:
            {sources_summary}
            
            Relevant Content Excerpts:
            {content_excerpts}
            
            Write a comprehensive section about "{section_title}" that:
            1. Synthesizes information from multiple sources
            2. Provides specific insights and analysis
            3. Maintains logical flow and structure
            4. Includes relevant citations [1], [2], etc.
            5. Is substantial and informative (aim for 400-800 words)
            
            Focus on creating original analysis and insights, not just compilation.""")
        ])
        
        # Create the synthesis chain
        self.synthesis_chain = (
            self.synthesis_prompt 
            | self.llm 
            | StrOutputParser()
        )
    
    def synthesize_section(self, section_title: str, relevant_docs: List[str], 
                          full_texts: List[str]) -> str:
        """
        Synthesize a research section using advanced AI analysis.
        
        Args:
            section_title: The section to write
            relevant_docs: List of relevant document excerpts
            full_texts: Full source texts for context
            
        Returns:
            str: Synthesized section content
        """
        print(f"🧠 AI Content Synthesizer: Analyzing sources for '{section_title}'...")
        
        # Prepare source summary
        sources_summary = f"Total sources: {len(full_texts)}, Relevant excerpts: {len(relevant_docs)}"
        
        # Get research context
        research_context = self.get_research_context()
        
        # Prepare content excerpts (limit to avoid token limits)
        content_excerpts = "\n\n".join([
            f"Source {i+1}: {doc[:500]}..." if len(doc) > 500 else f"Source {i+1}: {doc}"
            for i, doc in enumerate(relevant_docs[:5])  # Limit to 5 most relevant
        ])
        
        try:
            print(f"🔍 AI Processing: Analyzing {len(relevant_docs)} relevant sources...")
            
            # Execute the synthesis chain
            result = self.synthesis_chain.invoke({
                "section_title": section_title,
                "research_context": research_context,
                "sources_summary": sources_summary,
                "content_excerpts": content_excerpts
            })
            
            print(f"✅ AI Generated: {len(result)} characters of synthesized content")
            
            # Update research state
            if "generated_sections" not in self.research_state:
                self.research_state["generated_sections"] = []
            self.research_state["generated_sections"].append({
                "title": section_title,
                "length": len(result),
                "sources_used": len(relevant_docs)
            })
            
            return result
            
        except Exception as e:
            print(f"⚠️ Synthesis error: {e}")
            return self._fallback_synthesis(section_title, relevant_docs)
    
    def _fallback_synthesis(self, section_title: str, relevant_docs: List[str]) -> str:
        """Fallback synthesis method."""
        print("🔄 Using fallback synthesis method...")
        
        if not relevant_docs:
            return f"## {section_title}\n\nNo relevant content found for this section."
        
        # Simple concatenation with basic formatting
        content = f"Based on available sources:\n\n"
        for i, doc in enumerate(relevant_docs[:3]):
            content += f"{doc[:300]}...\n\n"
        
        return content

class QualityVerifier(EnhancedLLMCore):
    """
    Quality verification and fact-checking using LangChain.
    """
    
    def __init__(self):
        super().__init__()
        
        self.verification_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a quality assurance expert and fact-checker. Your job is to 
            analyze research content for accuracy, completeness, and quality.
            
            Evaluate content for:
            1. Factual accuracy and consistency
            2. Citation quality and completeness  
            3. Logical flow and coherence
            4. Completeness of coverage
            5. Potential biases or gaps
            
            Provide specific, actionable feedback."""),
            
            ("human", """Research Content to Verify:
            {content}
            
            Research Question: {question}
            
            Available Sources: {source_count} sources
            
            Please analyze this research for:
            1. Quality score (1-10)
            2. Missing citations or dangling references
            3. Content gaps or areas needing improvement
            4. Factual consistency issues
            5. Overall assessment and recommendations
            
            Return as JSON with keys: 'quality_score', 'issues', 'recommendations', 'missing_citations'""")
        ])
        
        self.verification_chain = (
            self.verification_prompt 
            | self.llm 
            | JsonOutputParser()
        )
    
    def verify_research_quality(self, content: str, question: str, source_count: int) -> Dict[str, Any]:
        """
        Verify research quality using AI analysis.
        
        Returns:
            Dict with quality assessment results
        """
        print(f"🔍 AI Quality Verifier: Analyzing research accuracy and completeness...")
        
        try:
            result = self.verification_chain.invoke({
                "content": content[:4000],  # Limit content for token management
                "question": question,
                "source_count": source_count
            })
            
            quality_score = result.get("quality_score", 7)
            issues = result.get("issues", [])
            recommendations = result.get("recommendations", [])
            missing_citations = result.get("missing_citations", [])
            
            print(f"📊 Quality Score: {quality_score}/10")
            if issues:
                print(f"⚠️ Issues Found: {len(issues)} quality concerns")
            if missing_citations:
                print(f"🔗 Citation Issues: {len(missing_citations)} missing references")
            
            return {
                "quality_score": quality_score,
                "issues": issues,
                "recommendations": recommendations,
                "missing_citations": missing_citations
            }
            
        except Exception as e:
            print(f"⚠️ Verification error: {e}")
            return {
                "quality_score": 7,
                "issues": [],
                "recommendations": ["Manual review recommended"],
                "missing_citations": []
            }

# Global instances for easy access
research_planner = ResearchPlanner()
content_synthesizer = ContentSynthesizer()
quality_verifier = QualityVerifier()

#!/usr/bin/env python3

import sys
from pathlib import Path

# Ensure project root is on the import path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

print("Testing LLM synthesis directly...")

try:
    from deep_crawler.llm.enhanced_core import content_synthesizer
    print("✅ ContentSynthesizer imported")
    
    # Test with simple data
    result = content_synthesizer.synthesize_section(
        section_title="Test Section", 
        relevant_docs=["Sample text about artificial intelligence and technology."],
        full_texts=["Sample text about artificial intelligence and technology."]
    )
    
    print(f"✅ SUCCESS: Generated {len(result)} characters")
    print(f"Content preview: {result[:200]}...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

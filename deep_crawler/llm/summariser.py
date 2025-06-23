from deep_crawler.llm.core import chat
import toml
import re
import textwrap
import faiss
import numpy as np
from pathlib import Path
from deep_crawler.indexing.embed_cache import get_vector

CFG = toml.load(Path(__file__).parents[2] / "config.toml")

SYS = (
    "You are an expert research writer. Using ONLY the provided numbered snippets, "
    "write a comprehensive, well-flowing section of 300-500 words. "
    "Write in a natural, engaging style without repetitive formatting. "
    "Vary your writing structure - sometimes use paragraphs, sometimes lists, "
    "sometimes subheadings as appropriate. Avoid formulaic 'Key Takeaways' sections. "
    "Instead, integrate important points naturally into the narrative. "
    "Always cite sources using [number] format."
)

TMPL = """SECTION: {title}

Available Information:
{snips}

Write a comprehensive, naturally-flowing section about this topic. Use varied paragraph structures and avoid repetitive formatting patterns. Make it informative, engaging, and well-researched.
"""

def rank(index, texts, query, k):
    qv = get_vector(query)
    qv = np.array([qv], dtype="float32")
    faiss.normalize_L2(qv)
    _, I = index.search(qv, k)
    return I[0]

def summarise_section(title, index, texts):
    I = rank(index, texts, title, CFG["index"]["snippets_per_sec"])
    # Increased snippet length for more detailed content
    sn = "\n".join(f"[{i+1}] {textwrap.shorten(texts[i], 500, placeholder='...')}" for i in I)
    # Increased max_tokens for longer, more detailed sections
    return chat(SYS, TMPL.format(title=title, snips=sn), max_tokens=800)

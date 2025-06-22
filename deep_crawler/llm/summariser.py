from llm.core import chat
import toml
import re
import textwrap
import faiss
import numpy as np
from pathlib import Path
from indexing.embed_cache import get_vector

CFG = toml.load(Path(__file__).parents[2] / "config.toml")

SYS = (
    "You are a domain expert. Using ONLY these numbered snippets, "
    "write the section (~180 words) then bullet key take-aways. "
    "Cite sources like [42]."
)

TMPL = """SECTION: {title}

Snippets:
{snips}

"""

def rank(index, texts, query, k):
    qv = get_vector(query)
    qv = np.array([qv], dtype="float32")
    faiss.normalize_L2(qv)
    _, I = index.search(qv, k)
    return I[0]

def summarise_section(title, index, texts):
    I = rank(index, texts, title, CFG["index"]["snippets_per_sec"])
    sn = "\n".join(f"[{i+1}] {textwrap.shorten(texts[i], 300)}" for i in I)
    return chat(SYS, TMPL.format(title=title, snips=sn), max_tokens=400)

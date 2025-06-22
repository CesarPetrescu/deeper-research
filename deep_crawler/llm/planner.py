from llm.core import chat
import xml.etree.ElementTree as ET

SYS = "You are a meticulous research planner. Return outline + XML keywords."
USR = """Topic: {q}

1. Output a Markdown outline with 3–6 H2 sections.
2. Provide 8–12 search keywords wrapped in:
<keywords><k>…</k></keywords>
"""

def plan(query):
    out = chat(SYS, USR.format(q=query), max_tokens=800)
    outline, xml_raw = out.split("<keywords", 1)
    root = ET.fromstring("<keywords" + xml_raw)
    kws = [k.text.strip() for k in root.findall("./k") if k.text]
    return outline.strip(), kws

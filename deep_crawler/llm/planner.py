from deep_crawler.llm.core import chat
import xml.etree.ElementTree as ET

SYS = "You are an expert research planner who creates comprehensive, well-structured outlines for in-depth research reports."

USR = """Topic: {q}

Create a detailed research plan with:

1. A comprehensive Markdown outline with 5-8 H2 sections that thoroughly cover the topic
2. Each section should be substantial enough to warrant 300-500 words of content
3. Include diverse angles: overview, features, benefits, comparisons, case studies, challenges, future outlook
4. Provide 12-16 targeted search keywords for comprehensive research

Format:
# [Topic Title]

## Section 1 Title
Brief description of what this section will cover

## Section 2 Title  
Brief description of what this section will cover

[continue for all sections]

<keywords>
<k>primary keyword</k>
<k>secondary keyword</k>
<k>specific feature keyword</k>
<k>comparison keyword</k>
<k>industry term</k>
[continue for 12-16 keywords]
</keywords>
"""

def plan(query):
    out = chat(SYS, USR.format(q=query), max_tokens=1200)
    outline, xml_raw = out.split("<keywords", 1)
    root = ET.fromstring("<keywords" + xml_raw)
    kws = [k.text.strip() for k in root.findall("./k") if k.text]
    return outline.strip(), kws

import re

def dangling_citations(markdown, id_set):
    cites = set(int(m) for m in re.findall(r"\[(\d+)]", markdown))
    return cites - id_set

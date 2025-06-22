import faiss
import numpy as np
import hashlib
import pickle
import os
from pathlib import Path
from .embed_cache import get_vector

def build(texts):
    vecs = np.vstack([get_vector(t) for t in texts]).astype("float32")
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    return index

def save(index, path):
    faiss.write_index(index, str(path))

def load(path):
    return faiss.read_index(str(path))

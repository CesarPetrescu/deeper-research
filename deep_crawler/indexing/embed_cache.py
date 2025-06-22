import sqlite3
import pickle
import hashlib
import os
from pathlib import Path
from llm.core import embed

DB_PATH = Path(__file__).parent / "embeddings.sqlite"
con = sqlite3.connect(DB_PATH)
con.execute(
    "CREATE TABLE IF NOT EXISTS vecs (hash TEXT PRIMARY KEY, vec BLOB)"
)
con.commit()

def get_vector(text):
    h = hashlib.sha256(text.encode()).hexdigest()
    cur = con.execute("SELECT vec FROM vecs WHERE hash=?", (h,))
    row = cur.fetchone()
    if row:
        return pickle.loads(row[0])

    vec, _ = embed(text)
    con.execute("INSERT OR REPLACE INTO vecs VALUES (?,?)", (h, pickle.dumps(vec)))
    con.commit()
    return vec

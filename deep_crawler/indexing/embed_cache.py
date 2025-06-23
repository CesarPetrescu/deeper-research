import sqlite3
import pickle
import hashlib
import os
import threading
from pathlib import Path
from deep_crawler.llm.core import embed

DB_PATH = Path(__file__).parent / "embeddings.sqlite"

# Thread-local storage for SQLite connections
_local = threading.local()

def get_connection():
    """Get a thread-local SQLite connection"""
    if not hasattr(_local, 'connection'):
        _local.connection = sqlite3.connect(DB_PATH)
        _local.connection.execute(
            "CREATE TABLE IF NOT EXISTS vecs (hash TEXT PRIMARY KEY, vec BLOB)"
        )
        _local.connection.commit()
    return _local.connection

def get_vector(text):
    con = get_connection()
    h = hashlib.sha256(text.encode()).hexdigest()
    cur = con.execute("SELECT vec FROM vecs WHERE hash=?", (h,))
    row = cur.fetchone()
    if row:
        return pickle.loads(row[0])

    vec, _ = embed(text)
    con.execute("INSERT OR REPLACE INTO vecs VALUES (?,?)", (h, pickle.dumps(vec)))
    con.commit()
    return vec

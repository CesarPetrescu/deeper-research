#!/usr/bin/env python3
"""
Database module for storing research reports persistently
"""
import sqlite3
import json
import threading
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "research_reports.db"

# Thread-local storage for SQLite connections
_local = threading.local()

def get_connection():
    """Get a thread-local SQLite connection"""
    if not hasattr(_local, 'connection'):
        _local.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.connection.row_factory = sqlite3.Row
        init_database(_local.connection)
    return _local.connection

def init_database(conn):
    """Initialize the database schema"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_reports (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            content TEXT,
            error TEXT,
            stream_output TEXT,
            generated_at TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def store_report(research_id, question, content=None, error=None, stream_output=None):
    """Store a research report in the database"""
    conn = get_connection()
    
    generated_at = datetime.now().isoformat()
    
    conn.execute("""
        INSERT OR REPLACE INTO research_reports 
        (id, question, content, error, stream_output, generated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (research_id, question, content, error, stream_output, generated_at))
    
    conn.commit()
    print(f"Stored report in database: {research_id}")

def get_report(research_id):
    """Retrieve a research report from the database"""
    conn = get_connection()
    
    cursor = conn.execute("""
        SELECT id, question, content, error, stream_output, generated_at, created_at
        FROM research_reports 
        WHERE id = ?
    """, (research_id,))
    
    row = cursor.fetchone()
    if row:
        return {
            'id': row['id'],
            'question': row['question'],
            'content': row['content'],
            'error': row['error'],
            'stream_output': row['stream_output'],
            'generated_at': row['generated_at'],
            'created_at': row['created_at']
        }
    return None

def list_reports(limit=50, offset=0):
    """List recent research reports"""
    conn = get_connection()
    
    cursor = conn.execute("""
        SELECT id, question, generated_at, created_at,
               CASE WHEN content IS NOT NULL THEN 1 ELSE 0 END as has_content,
               CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END as has_error
        FROM research_reports 
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    return [dict(row) for row in cursor.fetchall()]

def delete_report(research_id):
    """Delete a research report"""
    conn = get_connection()
    
    cursor = conn.execute("DELETE FROM research_reports WHERE id = ?", (research_id,))
    conn.commit()
    
    return cursor.rowcount > 0

def cleanup_old_reports(days=30):
    """Clean up reports older than specified days"""
    conn = get_connection()
    
    cursor = conn.execute("""
        DELETE FROM research_reports 
        WHERE created_at < datetime('now', '-{} days')
    """.format(days))
    conn.commit()
    
    return cursor.rowcount

if __name__ == "__main__":
    # Test the database
    init_database(get_connection())
    print(f"Database initialized at: {DB_PATH}")
    
    # Show recent reports
    reports = list_reports(10)
    print(f"Found {len(reports)} recent reports")
    for report in reports:
        status = "✓" if report['has_content'] else "✗" if report['has_error'] else "..."
        print(f"  {status} {report['question'][:50]}... ({report['created_at']})")

"""
Database module - Pure SQLite (no SQLAlchemy ORM)

Manages connection pool and initialization
"""

import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "../futureswar.db")


def init_db():
    """Initialize database with tables on startup"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create generations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            image_path TEXT NOT NULL,
            is_sfw BOOLEAN DEFAULT 1,
            flagged_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allow dict-like access to columns
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None):
    """Execute a query and return result"""
    with get_db() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor


def fetch_one(query: str, params: tuple = None):
    """Fetch a single row"""
    with get_db() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()


def fetch_all(query: str, params: tuple = None):
    """Fetch all rows"""
    with get_db() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
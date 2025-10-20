import sqlite3
from contextlib import contextmanager
from typing import Generator

from config import settings

DATABASE_URL = settings.DATABASE_URL


def init_db() -> None:
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            mime_type TEXT,
            size INTEGER NOT NULL,
            uploaded_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            session_id TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL, -- 'user' or 'assistant'
            content TEXT NOT NULL,  -- JSON object of content block
            message TEXT,  -- Optional human-readable message text
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        )
    """
    )

    conn.commit()
    conn.close()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: tuple = ()) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()


def execute_many(query: str, params: list[tuple]) -> None:
    """Execute a query with multiple parameter sets"""
    with get_db() as (conn, c):
        c.executemany(query, params)
        conn.commit()

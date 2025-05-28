import sqlite3
from pathlib import Path

DB_PATH = Path("perch.db")

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            cover_path TEXT,
            last_played TEXT,
            play_count INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()
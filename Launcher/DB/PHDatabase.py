import sqlite3
import shutil
from pathlib import Path
from Launcher.Utils.Utils import resource_path

# Determine paths for bundled DB and user-writable DB
bundle_db = Path(resource_path("perch.db"))
user_dir = Path.home() / ".perch"
user_dir.mkdir(exist_ok=True)
user_db = user_dir / "perch.db"
# If no user DB exists, copy the bundled template (if present)
if not user_db.exists():
    try:
        shutil.copy(bundle_db, user_db)
    except FileNotFoundError:
        # If bundled DB doesn't exist, SQLite will create a new one on first connect
        pass
DB_PATH = user_db

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
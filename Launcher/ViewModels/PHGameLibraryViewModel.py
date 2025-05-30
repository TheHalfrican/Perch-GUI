import sqlite3
import configparser
from pathlib import Path
from Launcher.DB.database import DB_PATH
from Launcher.Models.game import Game

class GameLibraryViewModel:
    def __init__(self):
        # Read scan folders from config.ini
        config = configparser.ConfigParser()
        config.read(Path(__file__).parents[2] / 'config.ini')
        folders = config.get('library', 'scan_folders', fallback='').split(';')
        self.scan_paths = [Path(p) for p in folders if p]

    def scan_library(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for folder in self.scan_paths:
            if not folder.exists():
                continue
            for ext in ('*.iso', '*.xex', '*.elf', '*.*'):
                for file in folder.rglob(ext):
                    title = file.stem
                    try:
                        cursor.execute(
                            "INSERT INTO games (title, file_path) VALUES (?, ?)" ,
                            (title, str(file))
                        )
                    except sqlite3.IntegrityError:
                        pass  # already in database
        conn.commit()
        conn.close()

    def get_all_games(self) -> list[Game]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, file_path, cover_path, last_played, play_count"
            " FROM games ORDER BY title ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [Game(*row) for row in rows]
import sqlite3
import configparser
from pathlib import Path
from Launcher.DB.PHDatabase import DB_PATH
from Launcher.Models.PHGameModel import PHGameModel

class GameLibraryViewModel:
    def __init__(self):
        # Load scan folders from config.ini
        config = configparser.ConfigParser()
        config.read(Path(__file__).parents[2] / 'config.ini')
        folders = config.get('library', 'scan_folders', fallback='').split(';')
        self.scan_paths = [Path(p) for p in folders if p]

    def scan_library(self):
        # Scan folders and insert any new game files into the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for folder in self.scan_paths:
            if not folder.exists():
                continue
            for ext in ('*.iso', '*.xex', '*.elf'):
                for file in folder.rglob(ext):
                    title = file.stem
                    try:
                        cursor.execute(
                            "INSERT INTO games (title, file_path) VALUES (?, ?)",
                            (title, str(file))
                        )
                    except sqlite3.IntegrityError:
                        pass  # Already in DB
        conn.commit()
        conn.close()

    def add_game(self, file_path: str):
        # Manually add a single game file
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        title = Path(file_path).stem
        try:
            cursor.execute(
                "INSERT INTO games (title, file_path) VALUES (?, ?)",
                (title, file_path)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Already in DB
        conn.close()

    def get_all_games(self) -> list[PHGameModel]:
        # Retrieve all games from the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, file_path, cover_path, last_played, play_count"
            " FROM games ORDER BY title ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [PHGameModel(*row) for row in rows]
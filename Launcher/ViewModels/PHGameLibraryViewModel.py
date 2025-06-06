import sqlite3
import configparser
from pathlib import Path
from Launcher.DB.PHDatabase import DB_PATH
from Launcher.Utils.Utils import get_user_config_path
from Launcher.Models.PHGameModel import PHGameModel

class GameLibraryViewModel:
    def __init__(self):
        # Load scan folders from config.ini
        config = configparser.ConfigParser()
        config.read(str(get_user_config_path()))
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

    def delete_game(self, game_id: int):
        """
        Remove a game from the database by its ID.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()
        conn.close()

    def update_cover(self, game_id: int, cover_path: str):
        """
        Update the cover_path for a game in the database.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE games SET cover_path = ? WHERE id = ?",
            (cover_path, game_id)
        )
        conn.commit()
        conn.close()

    def get_file_path(self, game_id: int) -> str:
        """Retrieve the file_path for a game by its ID."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM games WHERE id = ?", (game_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else ""
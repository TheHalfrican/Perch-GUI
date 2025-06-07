import subprocess
import os
import sys
import sqlite3
from Launcher.DB.PHDatabase import DB_PATH
from Launcher.Utils.Utils import get_user_config_path, launch_xenia_with_flags
import configparser

class GameListController:
    def __init__(self):
        # Load emulator path from config
        config = configparser.ConfigParser()
        config.read(str(get_user_config_path()))
        self.emulator_path = config.get('paths', 'xenia_path', fallback='')

    def fetch_games(self) -> list[tuple]:
        """
        Return a list of tuples (id, title, cover_path, last_played, play_count)
        by querying the database.  The ViewModel should filter these further if needed.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, cover_path, last_played, play_count FROM games ORDER BY title ASC"
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def launch_game(self, game_id: int):
        """Launch the given game ID via Xenia with flags."""
        file_path = self.get_file_path(game_id)
        if file_path:
            try:
                launch_xenia_with_flags(file_path)
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "Launch Error", str(e))
                return
            # Update play_count and last_played in the database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE games
                   SET play_count = play_count + 1,
                       last_played = datetime('now')
                 WHERE id = ?
                """, (game_id,)
            )
            conn.commit()
            conn.close()

    def reveal_in_file_browser(self, game_id: int):
        
       # Show the game file in Finder/Explorer/xdg-open depending on platform.
        
        file_path = self.get_file_path(game_id)
        if not file_path:
            return

        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', '-R', file_path])
        elif sys.platform.startswith('win'):
            subprocess.Popen(['explorer', f'/select,{file_path}'])
        else:
            subprocess.Popen(['xdg-open', os.path.dirname(file_path)])

    def set_cover(self, game_id: int, cover_path: str):
        
        # Update just the cover_path column for a given game_id.
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE games SET cover_path = ? WHERE id = ?",
            (cover_path, game_id)
        )
        conn.commit()
        conn.close()

    def delete_game(self, game_id: int):
        
        # Remove a game row from the database.
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()
        conn.close()

    def get_file_path(self, game_id: int) -> str:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM games WHERE id = ?", (game_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ""
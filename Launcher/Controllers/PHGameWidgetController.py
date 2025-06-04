# Launcher/Controllers/PHGameWidgetController.py
import os
import sys
import sqlite3
import subprocess
from pathlib import Path

from Launcher.DB.PHDatabase import DB_PATH
import configparser

class GameWidgetController:
    def __init__(self, game_id: int):
        self.game_id = game_id
        # load emulator path from config
        config = configparser.ConfigParser()
        config.read(Path(__file__).parents[2] / 'config.ini')
        self.emulator_path = config.get('paths', 'xenia_path', fallback='')

    def get_file_path(self) -> str:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM games WHERE id = ?", (self.game_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ''

    def launch_game(self):
        file_path = self.get_file_path()
        if file_path and self.emulator_path:
            subprocess.Popen([str(self.emulator_path), file_path])
            # Update play_count and last_played in the database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE games
                   SET play_count = play_count + 1,
                       last_played = datetime('now')
                 WHERE id = ?
                """, (self.game_id,)
            )
            conn.commit()
            conn.close()

    def reveal_in_file_browser(self):
        file_path = self.get_file_path()
        if not file_path:
            return
        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', '-R', file_path])
        elif sys.platform.startswith('win'):
            subprocess.Popen(['explorer', f'/select,{file_path}'])
        else:
            subprocess.Popen(['xdg-open', os.path.dirname(file_path)])

    def set_cover(self, cover_path: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE games SET cover_path = ? WHERE id = ?",
            (cover_path, self.game_id)
        )
        conn.commit()
        conn.close()

    def delete_game(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (self.game_id,))
        conn.commit()
        conn.close()
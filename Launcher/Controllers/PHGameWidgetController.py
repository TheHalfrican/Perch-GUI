# Launcher/Controllers/PHGameWidgetController.py
import os
import sys
import sqlite3
import subprocess
from pathlib import Path

from Launcher.DB.PHDatabase import DB_PATH
from Launcher.Utils.Utils import get_user_config_path, launch_xenia_with_flags
import configparser

class GameWidgetController:
    def __init__(self, game_id: int):
        self.game_id = game_id
        # load emulator path from config
        config = configparser.ConfigParser()
        config.read(str(get_user_config_path()))
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

    def remove_cover(self):
        """Remove the cover art for this game by setting cover_path to an empty string."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE games SET cover_path = '' WHERE id = ?",
            (self.game_id,)
        )
        conn.commit()
        conn.close()

    def delete_game(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (self.game_id,))
        conn.commit()
        conn.close()
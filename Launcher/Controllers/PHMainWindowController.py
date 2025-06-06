import subprocess
import os
import sys

from Launcher.ViewModels.PHMainWindowViewModel import MainWindowViewModel
from Launcher.DB.PHDatabase import DB_PATH
import sqlite3
from Launcher.Utils.Utils import launch_xenia_with_flags

class MainWindowController:
    def __init__(self, view_model: MainWindowViewModel):
        self.vm = view_model

    def add_games(self, paths: list[str]):
        
       # Add each game file path to the database via the GameLibraryViewModel, then refresh the ViewModel's game list.
        
        for p in paths:
            self.vm.game_library_vm.add_game(p)
        self.vm.refresh_games()

    def delete_game(self, game_id: int):
        
        # Remove a game from the database by ID, then refresh the game list.
        
        self.vm.game_library_vm.delete_game(game_id)
        self.vm.refresh_games()

    def set_cover(self, game_id: int, cover_path: str):
        
        # Update the cover_path for a given game ID, then refresh the game list.
        
        self.vm.game_library_vm.update_cover(game_id, cover_path)
        self.vm.refresh_games()

    def launch_game(self, game_id: int):
        """
       # Launch the game using the emulator path stored in the ViewModel.
        """
        file_path = self.vm.game_library_vm.get_file_path(game_id)
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
        
       # Show the game file in the system's file explorer (Finder, Explorer, or default).
        
        file_path = self.vm.game_library_vm.get_file_path(game_id)
        if not file_path:
            return

        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', '-R', file_path])
        elif sys.platform.startswith('win'):
            subprocess.Popen(['explorer', f'/select,{file_path}'])
        else:
            # Assume a Unix-like system with xdg-open
            subprocess.Popen(['xdg-open', os.path.dirname(file_path)])


import subprocess
import os
import sys

from Launcher.ViewModels.PHMainWindowViewModel import MainWindowViewModel
from Launcher.DB.PHDatabase import DB_PATH
import sqlite3

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
        
       # Launch the game using the emulator path stored in the ViewModel.
        
        file_path = self.vm.game_library_vm.get_file_path(game_id)
        if file_path:
            emulator_path = self.vm.game_library_vm.emulator_path if hasattr(self.vm.game_library_vm, 'emulator_path') else None
            # If ViewModel doesn't provide emulator_path directly, assume it's stored in config
            if not emulator_path:
                emulator_path = self.vm.config.get('paths', 'xenia_path', fallback=None)
            if emulator_path:
                subprocess.Popen([emulator_path, file_path])

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
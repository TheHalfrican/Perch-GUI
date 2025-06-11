import configparser
from pathlib import Path
from typing import List

from Launcher.ViewModels.PHGameLibraryViewModel import GameLibraryViewModel
from Launcher.Models.PHGameModel import PHGameModel
from Launcher.Utils.Utils import get_user_config_path

class MainWindowViewModel:
    def __init__(self):
        # Path to user-writable config.ini
        self.config_path = get_user_config_path()
        self.config = configparser.ConfigParser()
        # Ensure theme attribute always exists
        self.theme = 'System Default'
        if self.config_path.exists():
            self.config.read(str(self.config_path))
            # Load persisted theme (default to 'System Default')
            if self.config.has_section('appearance'):
                self.theme = self.config.get('appearance', 'theme', fallback='System Default')

        # Load UI settings
        self.cover_width = self._load_cover_width()
        self.cover_height = int(self.cover_width * 1.5)
        self.show_titles = self.config.getboolean('appearance', 'show_titles', fallback=True)
        # Load list_mode from INI (default to False)
        if self.config.has_section('ui'):
            self.list_mode = self.config.getboolean('ui', 'list_mode', fallback=False)
        else:
            self.list_mode = False
        self.current_filter = ''

        # Underlying game library VM for data access
        self.game_library_vm = GameLibraryViewModel()
        self.game_library_vm.scan_library()
        self._all_games = self.game_library_vm.get_all_games()

    def _load_cover_width(self) -> int:
        ini_path = self.config_path
        config = self.config
        if config.has_section('ui'):
            return config.getint('ui', 'cover_width', fallback=300)
        return 300

    def save_cover_width(self, new_width: int):
        if not self.config.has_section('ui'):
            self.config.add_section('ui')
        self.config.set('ui', 'cover_width', str(new_width))
        with open(self.config_path, 'w') as cfgfile:
            self.config.write(cfgfile)
        self.cover_width = new_width
        self.cover_height = int(new_width * 1.5)

    def set_show_titles(self, show: bool):
        if not self.config.has_section('appearance'):
            self.config.add_section('appearance')
        self.config.set('appearance', 'show_titles', str(show))
        with open(self.config_path, 'w') as cfgfile:
            self.config.write(cfgfile)
        self.show_titles = show

    def set_list_mode(self, is_list: bool):
        self.list_mode = is_list
        # Persist the preference
        if not self.config.has_section('ui'):
            self.config.add_section('ui')
        self.config.set('ui', 'list_mode', str(is_list))
        with open(self.config_path, 'w') as cfgfile:
            self.config.write(cfgfile)

    def set_filter(self, filter_text: str):
        self.current_filter = filter_text.lower().strip()

    def refresh_games(self):
        self.game_library_vm.scan_library()
        self._all_games = self.game_library_vm.get_all_games()

    def get_filtered_games(self) -> List[PHGameModel]:
        if not self.current_filter:
            return self._all_games
        return [g for g in self._all_games if self.current_filter in g.title.lower()]
# Launcher/ViewModels/PHSettingsViewModel.py
import configparser
from pathlib import Path

class SettingsDialogViewModel:
    def __init__(self):
        self.config_path = Path(__file__).parents[2] / 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

    @property
    def emulator_path(self) -> str:
        return self.config.get('paths', 'xenia_path', fallback='')

    @emulator_path.setter
    def emulator_path(self, value: str):
        if not self.config.has_section('paths'):
            self.config.add_section('paths')
        self.config.set('paths', 'xenia_path', value)
        self._write_config()

    @property
    def scan_folders(self) -> list[str]:
        raw = self.config.get('library', 'scan_folders', fallback='')
        return [p for p in raw.split(';') if p]

    @scan_folders.setter
    def scan_folders(self, folders: list[str]):
        if not self.config.has_section('library'):
            self.config.add_section('library')
        # Remove duplicates while preserving order
        unique_folders = []
        for f in folders:
            if f not in unique_folders:
                unique_folders.append(f)
        self.config.set('library', 'scan_folders', ';'.join(unique_folders))
        self._write_config()

    @property
    def theme(self) -> str:
        return self.config.get('appearance', 'theme', fallback='System Default')

    @theme.setter
    def theme(self, value: str):
        if not self.config.has_section('appearance'):
            self.config.add_section('appearance')
        self.config.set('appearance', 'theme', value)
        self._write_config()

    def _write_config(self):
        with open(self.config_path, 'w') as cfgfile:
            self.config.write(cfgfile)
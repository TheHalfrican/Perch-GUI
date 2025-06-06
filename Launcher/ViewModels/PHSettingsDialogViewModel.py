# Launcher/ViewModels/PHSettingsViewModel.py
import configparser
from pathlib import Path

class SettingsDialogViewModel:
    def __init__(self):
        # Load INI directly from project
        bundle_ini = Path(__file__).parents[2] / 'config.ini'
        self.config_path = bundle_ini

        # Load INI
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

    # ─── Custom Theme Colors ──────────────────────────────────────────────

    @property
    def custom_bg_color(self) -> str:
        return self.config.get("CustomTheme", "bg_color", fallback="")

    @custom_bg_color.setter
    def custom_bg_color(self, val: str):
        if not self.config.has_section("CustomTheme"):
            self.config.add_section("CustomTheme")
        self.config.set("CustomTheme", "bg_color", val)
        self._write_config()

    @property
    def custom_text_color(self) -> str:
        return self.config.get("CustomTheme", "text_color", fallback="")

    @custom_text_color.setter
    def custom_text_color(self, val: str):
        if not self.config.has_section("CustomTheme"):
            self.config.add_section("CustomTheme")
        self.config.set("CustomTheme", "text_color", val)
        self._write_config()

    @property
    def custom_accent_color(self) -> str:
        return self.config.get("CustomTheme", "accent_color", fallback="")

    @custom_accent_color.setter
    def custom_accent_color(self, val: str):
        if not self.config.has_section("CustomTheme"):
            self.config.add_section("CustomTheme")
        self.config.set("CustomTheme", "accent_color", val)
        self._write_config()
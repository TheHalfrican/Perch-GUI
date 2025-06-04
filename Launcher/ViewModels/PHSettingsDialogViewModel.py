# Launcher/ViewModels/PHSettingsViewModel.py
import configparser
import toml
from pathlib import Path

class SettingsDialogViewModel:
    def __init__(self):
        self.config_path = Path(__file__).parents[2] / 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        # Determine xenia.config.toml path based on emulator_path from INI
        emulator_path = self.config.get('paths', 'xenia_path', fallback='')
        if emulator_path:
            exe_dir = Path(emulator_path).parent
            self.toml_path = exe_dir / 'xenia.config.toml'
        else:
            self.toml_path = Path(__file__).parents[2] / 'xenia.config.toml'

        # Load or initialize TOML data for Xenia settings
        if self.toml_path.exists():
            self.toml_data = toml.loads(self.toml_path.read_text())
        else:
            self.toml_data = {}
        # Ensure all emulator sections exist
        for section in ["Master", "GPU", "Input", "Hacks", "CanaryVideo", "CanaryHacks"]:
            self.toml_data.setdefault(section, {})

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

    def _write_xenia_toml(self):
        self.toml_path.write_text(toml.dumps(self.toml_data))

    # ─── Master Section ──────────────────────────────────────────────────

    @property
    def license_mask(self) -> int:
        return self.toml_data["Master"].get("license_mask", 0)

    @license_mask.setter
    def license_mask(self, val: int):
        self.toml_data["Master"]["license_mask"] = val
        self._write_xenia_toml()

    @property
    def user_language(self) -> int:
        return self.toml_data["Master"].get("user_language", 1)

    @user_language.setter
    def user_language(self, val: int):
        self.toml_data["Master"]["user_language"] = val
        self._write_xenia_toml()

    @property
    def mount_cache(self) -> bool:
        return self.toml_data["Master"].get("mount_cache", False)

    @mount_cache.setter
    def mount_cache(self, val: bool):
        self.toml_data["Master"]["mount_cache"] = val
        self._write_xenia_toml()

    # ─── GPU Section ─────────────────────────────────────────────────────

    @property
    def renderer(self) -> str:
        return self.toml_data["GPU"].get("renderer", "any")

    @renderer.setter
    def renderer(self, val: str):
        self.toml_data["GPU"]["renderer"] = val
        self._write_xenia_toml()

    @property
    def allow_variable_refresh(self) -> bool:
        return self.toml_data["GPU"].get("allow_variable_refresh", False)

    @allow_variable_refresh.setter
    def allow_variable_refresh(self, val: bool):
        self.toml_data["GPU"]["allow_variable_refresh"] = val
        self._write_xenia_toml()

    @property
    def black_bars(self) -> bool:
        return self.toml_data["GPU"].get("black_bars", False)

    @black_bars.setter
    def black_bars(self, val: bool):
        self.toml_data["GPU"]["black_bars"] = val
        self._write_xenia_toml()

    # ─── Input (HID) Section ────────────────────────────────────────────

    @property
    def keyboard_mode(self) -> str:
        return self.toml_data["Input"].get("keyboard_mode", "XInput")

    @keyboard_mode.setter
    def keyboard_mode(self, val: str):
        self.toml_data["Input"]["keyboard_mode"] = val
        self._write_xenia_toml()

    @property
    def keyboard_slot(self) -> int:
        return self.toml_data["Input"].get("keyboard_slot", 0)

    @keyboard_slot.setter
    def keyboard_slot(self, val: int):
        self.toml_data["Input"]["keyboard_slot"] = val
        self._write_xenia_toml()

    # ─── Hacks Section ──────────────────────────────────────────────────

    @property
    def protect_zero(self) -> bool:
        return self.toml_data["Hacks"].get("protect_zero", False)

    @protect_zero.setter
    def protect_zero(self, val: bool):
        self.toml_data["Hacks"]["protect_zero"] = val
        self._write_xenia_toml()

    @property
    def break_on_unimplemented(self) -> bool:
        return self.toml_data["Hacks"].get("break_on_unimplemented", False)

    @break_on_unimplemented.setter
    def break_on_unimplemented(self, val: bool):
        self.toml_data["Hacks"]["break_on_unimplemented"] = val
        self._write_xenia_toml()

    # ─── Canary Video Section ───────────────────────────────────────────

    @property
    def vsync_fps(self) -> str:
        return self.toml_data["CanaryVideo"].get("vsync_fps", "off")

    @vsync_fps.setter
    def vsync_fps(self, val: str):
        self.toml_data["CanaryVideo"]["vsync_fps"] = val
        self._write_xenia_toml()

    @property
    def internal_resolution(self) -> str:
        return self.toml_data["CanaryVideo"].get("internal_resolution", "720p")

    @internal_resolution.setter
    def internal_resolution(self, val: str):
        self.toml_data["CanaryVideo"]["internal_resolution"] = val
        self._write_xenia_toml()

    @property
    def avpack(self) -> str:
        return self.toml_data["CanaryVideo"].get("avpack", "")

    @avpack.setter
    def avpack(self, val: str):
        self.toml_data["CanaryVideo"]["avpack"] = val
        self._write_xenia_toml()

    # ─── Canary Hacks Section ───────────────────────────────────────────

    @property
    def max_queued_frames(self) -> int:
        return self.toml_data["CanaryHacks"].get("max_queued_frames", 1)

    @max_queued_frames.setter
    def max_queued_frames(self, val: int):
        self.toml_data["CanaryHacks"]["max_queued_frames"] = val
        self._write_xenia_toml()

    def reset_emulator_settings(self):
        """
        Remove or reset only the emulator-related sections (Master, GPU, Input, Hacks,
        CanaryVideo, CanaryHacks) to their default values.
        """
        for section in ["Master", "GPU", "Input", "Hacks", "CanaryVideo", "CanaryHacks"]:
            if section in self.toml_data:
                del self.toml_data[section]
            self.toml_data.setdefault(section, {})
        self._write_xenia_toml()
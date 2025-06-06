import sys
import os
import subprocess
import configparser
from pathlib import Path

def resource_path(relative_path):
    # When using PyInstaller, sys._MEIPASS is the temporary unpack location
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def get_user_config_path():
    """
    Returns a Path to a user-writable config file (~/.perch/config.ini),
    creating the directory if necessary.
    """
    home = Path.home()
    cfg_dir = home / ".perch"
    cfg_dir.mkdir(exist_ok=True)
    return cfg_dir / "config.ini"


# --- Xenia launcher with flags ---
def launch_xenia_with_flags(game_path: str):
    """
    Reads the user’s config.ini, translates the relevant sections
    into Xenia command-line flags, and launches Xenia with the given game path.
    """
    # Determine where config.ini lives
    from Launcher.Utils.Utils import get_user_config_path
    ini_path = get_user_config_path()

    config = configparser.ConfigParser()
    config.read(str(ini_path))

    # Path to the Xenia executable
    xenia_exe = config.get("paths", "xenia_path", fallback="")
    if not xenia_exe or not Path(xenia_exe).exists():
        raise FileNotFoundError(f"Xenia executable not found: {xenia_exe}")

    # Choose config: user copy if exists, otherwise bundled template
    user_toml = Path.home() / ".perch" / "xenia.config.toml"
    if user_toml.exists():
        toml_path = user_toml
    else:
        toml_path = Path(resource_path("xenia-canary.config.toml"))

    # Build argument list: xenia path, game, and --config flag only
    args = [
        xenia_exe,
        str(game_path),
        f"--config={toml_path}"
    ]

    # Launch Xenia
    return subprocess.Popen(args)
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

    # GPU backend
    renderer = config.get("gpu", "renderer", fallback="any")  # e.g. "Vulkan", "OpenGL", etc.
    # VSync on/off
    vsync_on = config.getboolean("gpu", "allow_variable_refresh", fallback=False)
    # Internal resolution
    resolution = config.get("canary_video", "internal_resolution", fallback="720p")
    # Keyboard mode
    keyboard_mode = config.get("input", "keyboard_mode", fallback="XInput")

    # Build argument list: xenia path first, then game, then flags
    args = [xenia_exe, str(game_path)]
    args.append(f"--gpu={renderer}")
    args.append(f"--vsync={'true' if vsync_on else 'false'}")
    args.append(f"--res={resolution}")
    args.append(f"--keyboard-mode={keyboard_mode}")

    # Launch Xenia
    return subprocess.Popen(args)
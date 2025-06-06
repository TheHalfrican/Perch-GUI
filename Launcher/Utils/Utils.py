import sys
import os
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
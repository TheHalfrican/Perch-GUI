import sys
import os

def resource_path(relative_path):
    # When using PyInstaller, sys._MEIPASS is the temporary unpack location
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)
import configparser
from pathlib import Path
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from Launcher.ViewModels.PHSettingsDialogViewModel import SettingsDialogViewModel

def apply_theme(theme_name: str):
    """Apply the selected theme palette to the QApplication instance."""
    app = QApplication.instance()

    # Use Fusion style for consistency
    app.setStyle('Fusion')

    if theme_name == 'System Default':
        # Native palette
        app.setPalette(app.style().standardPalette())

    elif theme_name == 'Light':
        # Off-white/light theme
        light = QPalette()
        light.setColor(QPalette.Window, QColor(245, 245, 245))
        light.setColor(QPalette.WindowText, Qt.black)
        light.setColor(QPalette.Base, QColor(255, 255, 255))
        light.setColor(QPalette.Text, Qt.black)
        light.setColor(QPalette.Button, QColor(245, 245, 245))
        light.setColor(QPalette.ButtonText, Qt.black)
        light.setColor(QPalette.Highlight, QColor(128, 128, 128))
        light.setColor(QPalette.HighlightedText, Qt.white)
        app.setPalette(light)

    elif theme_name == 'Dark':
        # Pure black/dark theme
        dark = QPalette()
        dark.setColor(QPalette.Window, QColor(0, 0, 0))
        dark.setColor(QPalette.WindowText, Qt.white)
        dark.setColor(QPalette.Base, QColor(18, 18, 18))
        dark.setColor(QPalette.Text, Qt.white)
        dark.setColor(QPalette.Button, QColor(0, 0, 0))
        dark.setColor(QPalette.ButtonText, Qt.white)
        dark.setColor(QPalette.Highlight, QColor(64, 64, 64))
        dark.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(dark)

    elif theme_name == 'Xbox 360':
        # Classic Xbox 360 colors: grays, green highlights, orange accents
        xbox = QPalette()
        xbox.setColor(QPalette.Window, QColor(14, 122, 13))
        xbox.setColor(QPalette.WindowText, Qt.black)
        xbox.setColor(QPalette.Base, QColor(215, 215, 215))
        xbox.setColor(QPalette.Text, Qt.black)
        xbox.setColor(QPalette.Button, QColor(200, 200, 200))
        xbox.setColor(QPalette.ButtonText, Qt.black)
        # Xbox green for highlights
        xbox.setColor(QPalette.Highlight, QColor(16, 124, 16))
        xbox.setColor(QPalette.HighlightedText, Qt.white)
        # Orange for links/visited
        xbox.setColor(QPalette.Link, QColor(240, 115, 0))
        xbox.setColor(QPalette.LinkVisited, QColor(200, 80, 0))
        app.setPalette(xbox)

    elif theme_name == 'Lavender Teal':
        # Lavender and Teal theme
        lt = QPalette()
        # Lavender background
        lt.setColor(QPalette.Window, QColor(220, 208, 255))  # Lavender
        lt.setColor(QPalette.WindowText, QColor(  0,  51,  51))  # Teal-ish dark text
        lt.setColor(QPalette.Base, QColor(230, 230, 250))  # Light lavender
        lt.setColor(QPalette.Text, QColor(  0,  51,  51))
        lt.setColor(QPalette.Button, QColor(200, 200, 235))  # Muted lavender
        lt.setColor(QPalette.ButtonText, QColor(  0,  51,  51))
        # Teal highlights
        lt.setColor(QPalette.Highlight, QColor(  0, 128, 128))  # Teal
        lt.setColor(QPalette.HighlightedText, Qt.white)
        # Link colors (using teal)
        lt.setColor(QPalette.Link, QColor(  0, 150, 150))
        lt.setColor(QPalette.LinkVisited, QColor(  0, 120, 120))
        app.setPalette(lt)

    elif theme_name == 'Custom':
        # Load custom colors from settings
        vm = SettingsDialogViewModel()
        bg_color = vm.custom_bg_color or "#ffffff"
        text_color = vm.custom_text_color or "#000000"
        accent_color = vm.custom_accent_color or "#0078d7"

        custom = QPalette()
        custom.setColor(QPalette.Window, QColor(bg_color))
        custom.setColor(QPalette.WindowText, QColor(text_color))
        custom.setColor(QPalette.Base, QColor(bg_color))
        custom.setColor(QPalette.Text, QColor(text_color))
        custom.setColor(QPalette.Button, QColor(bg_color))
        custom.setColor(QPalette.ButtonText, QColor(text_color))
        custom.setColor(QPalette.Highlight, QColor(accent_color))
        custom.setColor(QPalette.HighlightedText, QColor(text_color))
        app.setPalette(custom)
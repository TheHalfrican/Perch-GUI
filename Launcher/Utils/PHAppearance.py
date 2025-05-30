import configparser
from pathlib import Path
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

def apply_theme(app: QApplication):
    """Apply the selected theme palette to the QApplication instance."""
    # Read theme from config.ini
    config = configparser.ConfigParser()
    config.read(Path(__file__).parents[2] / 'config.ini')
    theme = config.get('appearance', 'theme', fallback='System Default')

    # Use Fusion style for consistency
    app.setStyle('Fusion')

    if theme == 'System Default':
        # Native palette
        app.setPalette(app.style().standardPalette())

    elif theme == 'Light':
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

    elif theme == 'Dark':
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

    elif theme == 'Xbox 360':
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
import sqlite3
import subprocess
import configparser
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QMenu, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from Launcher.DB.PHDatabase import DB_PATH
from Launcher.Utils.PHImages import get_placeholder_pixmap

# Load Xenia path from config.ini
config = configparser.ConfigParser()
config.read(Path(__file__).parents[2] / 'config.ini')
XENIA_PATH = Path(config.get('paths', 'xenia_path'))

class GameWidgetView(QWidget):
    def __init__(self, game_id: int, title: str, cover_path: str | None = None, parent=None):
        super().__init__(parent)
        self.game_id = game_id
        self.title = title
        self.cover_path = cover_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(100, 100)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.set_cover(self.cover_path)

        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.cover_label)
        layout.addWidget(self.title_label)

    def set_cover(self, path: str | None):
        if path and Path(path).exists():
            pixmap = QPixmap(str(path))
        else:
            pixmap = get_placeholder_pixmap(100)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.cover_label.setPixmap(pixmap)
        self.cover_path = path

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        set_cover_action = menu.addAction("Set Cover Image...")
        remove_action = menu.addAction("Remove Game from Library")
        selected = menu.exec(event.globalPos())

        if selected == set_cover_action:
            img_path, _ = QFileDialog.getOpenFileName(
                self, "Choose Cover Image", "", "Image Files (*.png *.jpg *.bmp)"
            )
            if img_path:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE games SET cover_path = ? WHERE id = ?",
                    (img_path, self.game_id)
                )
                conn.commit()
                conn.close()
                self.set_cover(img_path)

        elif selected == remove_action:
            confirm = QMessageBox.question(
                self, "Confirm Remove",
                f"Remove '{self.title}' from library?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM games WHERE id = ?", (self.game_id,))
                conn.commit()
                conn.close()
                # Remove widget from UI
                self.setParent(None)

    def mouseDoubleClickEvent(self, event):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM games WHERE id = ?", (self.game_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            subprocess.Popen([str(XENIA_PATH), row[0]])

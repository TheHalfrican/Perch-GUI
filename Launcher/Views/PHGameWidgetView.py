# Launcher/Views/PHGameWidgetView.py
import sys
import subprocess
import configparser
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QMenu, QMessageBox
from PySide6.QtGui import QPixmap, QGuiApplication, QDesktopServices
from PySide6.QtCore import Qt, Signal, QUrl

from Launcher.Utils.PHImages import get_placeholder_pixmap
from Launcher.Utils.Utils import get_user_config_path
from Launcher.Controllers.PHGameWidgetController import GameWidgetController

# Load Xenia path from config.ini
config = configparser.ConfigParser()
config.read(str(get_user_config_path()))
# Safely get xenia_path; if no [paths] section, default to empty
if config.has_section('paths'):
    xenia_path_str = config.get('paths', 'xenia_path', fallback="")
else:
    xenia_path_str = ""
XENIA_PATH = Path(xenia_path_str)

class GameWidgetView(QWidget):
    clicked = Signal(object)
    def __init__(self, game_id: int, title: str, cover_path: str | None = None,
                 cover_width: int = 300, cover_height: int = 450, parent=None):
        super().__init__(parent)
        self.game_id = game_id

        # Instantiate Controller for this Widget
        self.controller = GameWidgetController(self.game_id)

        self.title = title
        self.cover_path = cover_path
        self.cover_width = cover_width
        self.cover_height = cover_height
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(self.cover_width, self.cover_height)
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
            pixmap = get_placeholder_pixmap(self.cover_width, self.cover_height)
        # Scale at device pixel ratio for crisp rendering
        dpr = QGuiApplication.primaryScreen().devicePixelRatio()
        target_width = int(self.cover_width * dpr)
        target_height = int(self.cover_height * dpr)
        high_res = pixmap.scaled(
            target_width, target_height,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        high_res.setDevicePixelRatio(dpr)
        # Set on label at logical size
        self.cover_label.setPixmap(high_res)
        self.cover_label.setFixedSize(self.cover_width, self.cover_height)
        self.cover_path = path


    def contextMenuEvent(self, event):
        menu = QMenu(self)
        launch_action = menu.addAction("Launch Game")
        show_action = menu.addAction("Show in File Browser")
        set_cover_action = menu.addAction("Set Cover Image...")
        remove_cover_img_action = menu.addAction("Remove Cover Image")
        remove_action = menu.addAction("Remove Game from Library")
        selected = menu.exec(event.globalPos())

        if selected == launch_action:
            self.controller.launch_game()

        elif selected == show_action:
            # Reveal the game file in the OS file browser
            file_path = self.controller.get_file_path()
            if not file_path:
                return
            fp = Path(file_path)
            if sys.platform.startswith('darwin'):
                # macOS: open folder
                subprocess.Popen(['open', fp.parent])
            elif sys.platform.startswith('win'):
                # Windows: open Explorer and select file
                subprocess.Popen(['explorer', '/select,', str(fp)])
            else:
                # Linux/other: open containing folder
                
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(fp.parent)))

        elif selected == set_cover_action:
            img_path, _ = QFileDialog.getOpenFileName(
                self, "Choose Cover Image", "",
                "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
            )
            if img_path:
                self.controller.set_cover(img_path)
                self.cover_path = img_path
                self.set_cover(img_path)

        elif selected == remove_cover_img_action:
            self.controller.remove_cover()
            # Update UI to show placeholder
            self.cover_path = None
            self.set_cover(None)

        elif selected == remove_action:
            confirm = QMessageBox.question(
                self, "Confirm Remove",
                f"Remove '{self.title}' from library?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.controller.delete_game()
                self.setParent(None)

    def mouseDoubleClickEvent(self, event):
        file_path = self.controller.get_file_path()
        if file_path:
            subprocess.Popen([str(XENIA_PATH), file_path])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)
        super().mousePressEvent(event)

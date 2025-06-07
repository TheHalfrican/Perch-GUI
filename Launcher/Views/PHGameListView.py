import sys
import subprocess
from pathlib import Path
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenu, QFileDialog, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from Launcher.Controllers.PHGameListController import GameListController

class GameListView(QWidget):
    def __init__(self, parent=None, cover_size: QSize = QSize(64, 96)):
        super().__init__(parent)
        self.cover_size = cover_size

        # Instantiate controller
        self.controller = GameListController()

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Cover", "Title", "Last Played", "Play Count"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setIconSize(self.cover_size)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_context_menu)

        # Connect double-click to launch game when in first two columns
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        self.refresh_list()

    def refresh_list(self, filter_text: str = ""):
        # Fetch all games via controller
        rows = self.controller.fetch_games()

        # Filter rows if a filter text is provided
        if filter_text:
            rows = [r for r in rows if filter_text.lower() in r[1].lower()]

        self.table.setRowCount(len(rows))
        for row_idx, (game_id, title, cover_path, last_played, play_count) in enumerate(rows):
            # Cover art column
            if cover_path and cover_path.strip():
                pixmap = QPixmap(str(cover_path))
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(
                        self.cover_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    ))
                else:
                    icon = QIcon()
            else:
                icon = QIcon()

            cover_item = QTableWidgetItem()
            cover_item.setIcon(icon)
            cover_item.setText("")  # No text in cover column
            cover_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, cover_item)

            # Title column
            title_item = QTableWidgetItem(title)
            title_item.setData(Qt.UserRole, game_id)
            self.table.setItem(row_idx, 1, title_item)

            # Last played column
            last_item = QTableWidgetItem(last_played if last_played else "")
            last_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, last_item)

            # Play count column
            count_item = QTableWidgetItem(str(play_count))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, count_item)

        # Adjust row heights to fit cover size
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, self.cover_size.height() + 8)

    def on_context_menu(self, position):
        # Determine the row that was clicked
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        # Retrieve game_id from the title column (column 1)
        item = self.table.item(row, 1)
        game_id = item.data(Qt.UserRole)
        menu = QMenu(self)
        launch_action = menu.addAction("Launch Game")
        show_action = menu.addAction("Show in File Browser")
        set_cover_action = menu.addAction("Set Cover Image...")
        remove_action = menu.addAction("Remove Game from Library")
        selected = menu.exec(self.table.viewport().mapToGlobal(position))

        if selected == launch_action:
            self.controller.launch_game(game_id)

        elif selected == show_action:
            # Reveal the game file in OS file browser
            file_path = self.controller.get_file_path(game_id)
            if not file_path:
                return
            fp = Path(file_path)
            if sys.platform.startswith('darwin'):
                subprocess.Popen(['open', str(fp.parent)])
            elif sys.platform.startswith('win'):
                subprocess.Popen(['explorer', '/select,', str(fp)])
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(fp.parent)))

        elif selected == set_cover_action:
            img_path, _ = QFileDialog.getOpenFileName(
                self, "Choose Cover Image", "",
                "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
            )
            if img_path:
                self.controller.set_cover(game_id, img_path)
                # Refresh list to show new cover
                self.refresh_list()

        elif selected == remove_action:
            confirm = QMessageBox.question(
                self, "Confirm Remove",
                "Remove this game from library?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.controller.delete_game(game_id)
                # Refresh list after removal
                self.refresh_list()

    def on_cell_double_clicked(self, row: int, column: int):
        # Only launch if double-clicked in cover (col 0) or title (col 1)
        if column in (0, 1):
            item = self.table.item(row, 1)
            game_id = item.data(Qt.UserRole)
            self.controller.launch_game(game_id)
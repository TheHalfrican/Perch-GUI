

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
import sqlite3
from Launcher.DB.PHDatabase import DB_PATH

class GameListView(QWidget):
    def __init__(self, parent=None, cover_size: QSize = QSize(64, 96)):
        super().__init__(parent)
        self.cover_size = cover_size

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

        self.refresh_list()

    def refresh_list(self, filter_text: str = ""):
        # Fetch games from the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, cover_path, last_played, play_count FROM games ORDER BY title ASC"
        )
        rows = cursor.fetchall()
        conn.close()

        # Filter rows if a filter text is provided
        if filter_text:
            rows = [r for r in rows if filter_text.lower() in r[0].lower()]

        self.table.setRowCount(len(rows))
        for row_idx, (title, cover_path, last_played, play_count) in enumerate(rows):
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
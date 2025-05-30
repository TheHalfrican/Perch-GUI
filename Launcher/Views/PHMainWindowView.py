import configparser
from pathlib import Path
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QScrollArea,
    QWidget, QGridLayout, QLabel
)
from PySide6.QtCore import Qt
from Launcher.ViewModels.PHGameLibraryViewModel import GameLibraryViewModel
from Launcher.Views.PHGameWidgetView import GameWidget

class PerchLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Perch - Game Library")
        self.resize(800, 600)

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        add_action = QAction("Add Game...", self)
        add_action.triggered.connect(self.add_game)
        file_menu.addAction(add_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ViewModel
        self.viewmodel = GameLibraryViewModel()
        self.viewmodel.scan_library()

        # Central Widget & Layout
        self.container = QWidget()
        self.layout = QGridLayout(self.container)
        self.layout.setSpacing(10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        self.setCentralWidget(self.scroll)

        # Initial population
        self.populate_grid()

    def populate_grid(self):
        # Clear existing items
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        games = self.viewmodel.get_all_games()
        if not games:
            label = QLabel(
                "No games found. Use File > Add Game... to add titles."
            )
            label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(label, 0, 0)
            return

        cols = 6
        row = col = 0
        for game in games:
            widget = GameWidget(game.id, game.title, game.cover_path)
            self.layout.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def add_game(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Game Files", "", "Xbox 360 Files (*.iso *.xex *.elf *.*)"
        )
        if not paths:
            return
        for p in paths:
            self.viewmodel.add_game(p)
        self.populate_grid()
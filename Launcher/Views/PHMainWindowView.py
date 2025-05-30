import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QScrollArea,
    QWidget, QGridLayout, QLabel, QSlider, QVBoxLayout
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt
from Launcher.ViewModels.PHGameLibraryViewModel import GameLibraryViewModel
from Launcher.Views.PHGameWidgetView import GameWidgetView

class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Perch - Game Library")
        self.resize(1000, 800)

        # Cover size controls
        self.cover_width = 300
        self.cover_height = 450
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(100)
        self.slider.setMaximum(600)
        self.slider.setSingleStep(50)
        self.slider.setTickInterval(100)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setValue(self.cover_width)
        self.slider.valueChanged.connect(self.on_slider_value_changed)

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

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Slider label
        self.slider_label = QLabel(f"Cover Size: {self.cover_width}×{self.cover_height}px")
        self.slider_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.slider_label)
        main_layout.addWidget(self.slider)

        # Scrollable grid container
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(10)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        self.setCentralWidget(main_widget)
        self.populate_grid()

    def populate_grid(self):
        # Clear grid
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        games = self.viewmodel.get_all_games()
        if not games:
            label = QLabel("No games found. Use File > Add Game... to add titles.")
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, 0, 0)
            return

        cols = 6
        row = col = 0
        for game in games:
            widget = GameWidgetView(
                game.id, game.title, game.cover_path,
                self.cover_width, self.cover_height
            )
            self.grid.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def on_slider_value_changed(self, value):
        self.cover_width = value
        self.cover_height = int(value * 1.5)
        self.slider_label.setText(f"Cover Size: {self.cover_width}×{self.cover_height}px")
        self.populate_grid()

    def add_game(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Game Files", "", "Xbox 360 Files (*.iso *.xex *.elf)"
        )
        if not paths:
            return
        for p in paths:
            self.viewmodel.add_game(p)
        self.populate_grid()
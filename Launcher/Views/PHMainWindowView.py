# Launcher/Views/PHMainWindowView.py
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QScrollArea,
    QWidget, QGridLayout, QLabel, QSlider,
    QVBoxLayout, QHBoxLayout, QApplication, QDialog,
    QLineEdit, QPushButton
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize
from Launcher.ViewModels.PHGameLibraryViewModel import GameLibraryViewModel
from Launcher.Views.PHGameWidgetView import GameWidgetView
from Launcher.Views.PHGameListView import GameListView
from Launcher.Views.PHSettingsDialogView import SettingsDialog
from Launcher.Utils.PHAppearance import apply_theme

class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Perch - Game Library")
        self.resize(1000, 800)

        # Apply the selected theme
        apply_theme(QApplication.instance())

        # Flag for showing/hiding titles
        self.show_titles = True

        # Track current view mode: False = grid, True = list
        self.list_mode = False

        # Cover size slider: width 100-600px (height auto 1.5x)
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

        # Search bar for filtering
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search games...")
        self.search_bar.textChanged.connect(lambda _: self.populate_grid())

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        add_action = QAction("Add Game...", self)
        add_action.triggered.connect(self.add_game)
        file_menu.addAction(add_action)
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        toggle_titles = QAction("Show Titles", self, checkable=True)
        toggle_titles.setChecked(True)
        toggle_titles.triggered.connect(self.on_toggle_titles)
        view_menu.addAction(toggle_titles)

        # ViewModel
        self.viewmodel = GameLibraryViewModel()
        self.viewmodel.scan_library()

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        slider_layout = QHBoxLayout()
        slider_layout.addStretch()
        slider_layout.addWidget(self.slider)
        main_layout.addLayout(slider_layout)
        self.slider.setFixedWidth(self.width() // 4)

        # View mode buttons
        view_buttons_layout = QHBoxLayout()
        # Grid button
        self.grid_button = QPushButton()
        self.grid_button.setIcon(QIcon('assets/grid_icon.png'))
        self.grid_button.setToolTip("Grid View")
        self.grid_button.setFixedSize(48, 48)
        self.grid_button.setIconSize(QSize(48, 48))
        self.grid_button.clicked.connect(self.populate_grid)
        view_buttons_layout.addWidget(self.grid_button)
        # List button
        self.list_button = QPushButton()
        self.list_button.setIcon(QIcon('assets/list_icon.png'))
        self.list_button.setToolTip("List View")
        self.list_button.setFixedSize(48, 48)
        self.list_button.setIconSize(QSize(48, 48))
        self.list_button.clicked.connect(self.populate_list)
        view_buttons_layout.addWidget(self.list_button)
        # Align buttons to left
        view_buttons_layout.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(view_buttons_layout)
        main_layout.addWidget(self.search_bar)


        # Scrollable grid container
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(10)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        main_layout.addWidget(self.scroll)

        # Create the list view container before populating
        self.list_view = GameListView(self)
        self.list_view.setVisible(False)
        main_layout.addWidget(self.list_view)

        self.setCentralWidget(main_widget)
        self.populate_grid()

    def on_toggle_titles(self, checked: bool):
        self.show_titles = checked
        self.populate_grid()

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            apply_theme(QApplication.instance())
            self.viewmodel = GameLibraryViewModel()
            self.viewmodel.scan_library()
            self.populate_grid()

    def populate_grid(self):
        # Show grid, hide list view
        self.scroll.setVisible(True)
        self.list_view.setVisible(False)
        # Show slider in grid view
        self.slider.setVisible(True)

        self.list_mode = False

        # Clear existing items
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        games = self.viewmodel.get_all_games()
        # Filter by search text
        text = self.search_bar.text().lower().strip()
        if text:
            games = [g for g in games if text in g.title.lower()]

        # Placeholder when no games
        if not games:
            msg = "No games match your search." if text else "No games found. Use File > Add Game..."
            label = QLabel(msg)
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, 0, 0)
            return

        # Calculate columns based on viewport width
        spacing = self.grid.spacing()
        w = self.scroll.viewport().width()
        cols = max(1, (w + spacing) // (self.cover_width + spacing))

        row = col = 0
        for game in games:
            widget = GameWidgetView(
                game.id, game.title, game.cover_path,
                self.cover_width, self.cover_height
            )
            # Show or hide title below cover
            widget.title_label.setVisible(self.show_titles)

            self.grid.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.slider.setFixedWidth(self.width() // 4)
        if self.list_mode:
            # Refresh list view without switching to grid
            filter_text = self.search_bar.text().lower().strip()
            self.list_view.refresh_list(filter_text)
        else:
            self.populate_grid()

    def on_slider_value_changed(self, value: int):
        self.cover_width = value
        self.cover_height = int(value * 1.5)
        self.populate_grid()

    def add_game(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Game Files", "", "Xbox 360 Files (*.iso *.xex *.elf);;All Files (*)"
        )
        if not paths:
            return
        for p in paths:
            self.viewmodel.add_game(p)
        self.populate_grid()

    def populate_list(self):
        # Show list view, hide grid
        self.scroll.setVisible(False)
        self.list_view.setVisible(True)
        # Hide slider in list view
        self.slider.setVisible(False)

        self.list_mode = True

        # Refresh list view with current search filter
        filter_text = self.search_bar.text().lower().strip()
        self.list_view.refresh_list(filter_text)

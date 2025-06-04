# Launcher/Views/PHMainWindowView.py
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QScrollArea,
    QWidget, QGridLayout, QLabel, QSlider,
    QVBoxLayout, QHBoxLayout, QApplication, QDialog,
    QLineEdit, QPushButton
)
from PySide6.QtGui import QAction, QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QSize, QFileSystemWatcher
from Launcher.ViewModels.PHMainWindowViewModel import MainWindowViewModel
from Launcher.ViewModels.PHSettingsDialogViewModel import SettingsDialogViewModel
from Launcher.Views.PHGameWidgetView import GameWidgetView
from Launcher.Views.PHGameListView import GameListView
from Launcher.Views.PHSettingsDialogView import SettingsDialog
from Launcher.Views.PHGamepadConfigView import GamepadConfigView
from Launcher.Utils.PHAppearance import apply_theme
from Launcher.Controllers.PHMainWindowController import MainWindowController

class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Perch - Game Library")
        self.resize(1000, 800)

        self.current_selected_widget = None
        # Instantiate ViewModel
        self.vm = MainWindowViewModel()
        # Instantiate Controller
        self.controller = MainWindowController(self.vm)

        # ─── Watch Folders for Automatic Library Refresh ───────────────────
        self.fs_watcher = QFileSystemWatcher(self)
        # Start by watching all scan‐folders in the ViewModel
        self._reset_watch_paths()

        # Whenever any watched directory changes (new file/ISO added, renamed, or removed),
        # trigger a library refresh
        self.fs_watcher.directoryChanged.connect(self._on_folder_changed)
        self.fs_watcher.fileChanged.connect(self._on_folder_changed)

        # Apply the selected theme
        apply_theme(QApplication.instance())

        # Initialize cover dimensions from ViewModel
        self.cover_width = self.vm.cover_width
        self.cover_height = self.vm.cover_height
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(100)
        self.slider.setMaximum(600)
        self.slider.setSingleStep(50)
        self.slider.setTickInterval(100)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setValue(self.vm.cover_width)
        self.slider.valueChanged.connect(self.on_slider_value_changed)

        # Search bar for filtering
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search games...")
        self.search_bar.textChanged.connect(lambda _: self.populate_grid())
        # Adjust placeholder text color based on theme via palette
        current_theme = self.vm.config.get('appearance', 'theme', fallback='System Default')
        palette = self.search_bar.palette()
        if current_theme == 'Dark':
            # White text and light gray placeholder on dark background
            self.search_bar.setStyleSheet("QLineEdit { color: white; }")
            palette.setColor(QPalette.PlaceholderText, QColor("lightgray"))
        else:
            # Black text and dark gray placeholder on light background
            self.search_bar.setStyleSheet("QLineEdit { color: black; }")
            palette.setColor(QPalette.PlaceholderText, QColor("darkgray"))
        self.search_bar.setPalette(palette)

        # Menu Bar
        menubar = self.menuBar()
        # System menu
        system_menu = menubar.addMenu("System")
        file_menu = menubar.addMenu("File")
        add_action = QAction("Add Game...", self)
        add_action.triggered.connect(self.add_game)
        file_menu.addAction(add_action)
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.open_settings)
        system_menu.addAction(settings_action)
        input_action = QAction("Controller Settings...", self)
        input_action.triggered.connect(self.open_gamepad_config)
        system_menu.addAction(input_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        toggle_titles = QAction("Show Titles", self, checkable=True)
        toggle_titles.setChecked(self.vm.show_titles)
        toggle_titles.triggered.connect(self.on_toggle_titles)
        view_menu.addAction(toggle_titles)

        # Add Grid/List view options to the View menu
        grid_action = QAction("Grid View", self)
        grid_action.triggered.connect(self.populate_grid)
        view_menu.addAction(grid_action)

        list_action = QAction("List View", self)
        list_action.triggered.connect(self.populate_list)
        view_menu.addAction(list_action)

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # --- Top row layout: view buttons + slider, slider right of buttons, stretch at end ---
        top_row_layout = QHBoxLayout()

        # View mode buttons
        view_buttons_layout = QHBoxLayout()
        # Settings Button
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon("Assets/settings_icon.png"))
        self.settings_button.setToolTip("Settings")
        self.settings_button.setFixedSize(48, 48)
        self.settings_button.setIconSize(QSize(48, 48))
        self.settings_button.clicked.connect(self.open_settings)
        view_buttons_layout.addWidget(self.settings_button)
        # Controller Configuration Button
        self.controller_config_button = QPushButton()
        self.controller_config_button.setIcon(QIcon("Assets/controller_config_icon.png"))
        self.controller_config_button.setToolTip("Controller Config")
        self.controller_config_button.setFixedSize(48, 48)
        self.controller_config_button.setIconSize(QSize(48, 48))
        self.controller_config_button.clicked.connect(self.open_gamepad_config)
        view_buttons_layout.addWidget(self.controller_config_button)
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
        # Game Titles toggle button
        self.title_toggle_button = QPushButton()
        self.title_toggle_button.setIcon(QIcon('assets/tag_icon.png'))
        self.title_toggle_button.setToolTip("Toggle Game Titles")
        self.title_toggle_button.setFixedSize(48, 48)
        self.title_toggle_button.setIconSize(QSize(48, 48))
        self.title_toggle_button.setCheckable(True)
        self.title_toggle_button.setChecked(self.vm.show_titles)
        self.title_toggle_button.toggled.connect(self.on_toggle_titles)
        view_buttons_layout.addWidget(self.title_toggle_button)
        # Align buttons to left
        view_buttons_layout.setAlignment(Qt.AlignLeft)

        top_row_layout.addLayout(view_buttons_layout)
        top_row_layout.addWidget(self.slider)
        self.slider.setFixedWidth(self.width() // 4)
        top_row_layout.addStretch()

        main_layout.addLayout(top_row_layout)

        # Search bar layout: right-aligned, one quarter window width
        search_layout = QHBoxLayout()
        search_layout.addStretch()
        search_layout.addWidget(self.search_bar)
        self.search_bar.setFixedWidth(self.width() // 4)
        main_layout.addLayout(search_layout)


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
        self.vm.set_show_titles(checked)
        self.populate_grid()

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            apply_theme(QApplication.instance())
            self.vm = MainWindowViewModel()
            # Re-watch whatever folder the user just saved
            self._reset_watch_paths()
         # Update search bar placeholder color … 
            self.populate_grid()
            # Update search bar placeholder color after theme change
            new_theme = self.vm.config.get('appearance', 'theme', fallback='System Default')
            palette = self.search_bar.palette()
            if new_theme == 'Dark':
                self.search_bar.setStyleSheet("QLineEdit { color: white; }")
                palette.setColor(QPalette.PlaceholderText, QColor("lightgray"))
            else:
                self.search_bar.setStyleSheet("QLineEdit { color: black; }")
                palette.setColor(QPalette.PlaceholderText, QColor("darkgray"))
            self.search_bar.setPalette(palette)
            self.populate_grid()

    def populate_grid(self):
        self.vm.set_list_mode(False)
        # Show grid, hide list view
        self.scroll.setVisible(True)
        self.list_view.setVisible(False)
        # Show slider in grid view
        self.slider.setVisible(True)

        # Clear existing items
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Update filter text in VM
        self.vm.set_filter(self.search_bar.text())
        games = self.vm.get_filtered_games()

        # Placeholder when no games
        text = self.search_bar.text().lower().strip()
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
            widget.title_label.setVisible(self.vm.show_titles)
            # Connect click signal to selection handler
            widget.clicked.connect(self.on_game_clicked)
            self.grid.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.slider.setFixedWidth(self.width() // 4)
        self.search_bar.setFixedWidth(self.width() // 4)
        if self.vm.list_mode:
            # Refresh list view without switching to grid
            self.list_view.refresh_list(self.vm.current_filter)
        else:
            self.populate_grid()

    def on_slider_value_changed(self, value: int):
        self.cover_width = value
        self.cover_height = int(value * 1.5)
        # Save cover_width via ViewModel
        self.vm.save_cover_width(value)
        self.populate_grid()

    def add_game(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Game Files", "", "Xbox 360 Files (*.iso *.xex *.elf);;All Files (*)"
        )
        if not paths:
            return
        self.controller.add_games(paths)
        self.populate_grid()

    def populate_list(self):
        self.vm.set_list_mode(True)
        self.vm.set_filter(self.search_bar.text())
        self.vm.refresh_games()
        # Hide grid and slider, show list view
        self.scroll.setVisible(False)
        self.list_view.setVisible(True)
        self.slider.setVisible(False)
        self.list_view.refresh_list(self.vm.current_filter)

    def on_game_clicked(self, widget):
        # Clear previous highlight
        if self.current_selected_widget and self.current_selected_widget is not widget:
            self.current_selected_widget.setStyleSheet("")
        # Highlight new selection
        widget.setStyleSheet("border: 2px solid #FFD700;")
        self.current_selected_widget = widget

    def open_gamepad_config(self):
        dialog = GamepadConfigView(self)
        dialog.exec()

    def _reset_watch_paths(self):
        """
        Replace the QFileSystemWatcher’s watched paths with the current scan_folders from settings.
        """
        # Remove old paths
        for p in self.fs_watcher.directories():
            self.fs_watcher.removePath(p)
        for f in self.fs_watcher.files():
            self.fs_watcher.removePath(f)

        # Load scan folders from Settings ViewModel
        settings_vm = SettingsDialogViewModel()
        for folder in settings_vm.scan_folders:
            try:
                folder_path = Path(folder)
                if not folder_path.exists() or not folder_path.is_dir():
                    continue
                # Watch the folder itself
                self.fs_watcher.addPath(folder)
                # Also watch each file inside
                for child in folder_path.iterdir():
                    if child.is_file():
                        self.fs_watcher.addPath(str(child))
            except Exception:
                # Skip any paths that cause errors (e.g., invalid paths)
                continue

    def _on_folder_changed(self, path):
        """
        Called whenever a watched directory/file changes on disk.
        Refresh the VM’s game list and repopulate whichever view is visible.
        """
        # Rescan the library, update VM, then re-render
        self.vm.refresh_games()
        if self.vm.list_mode:
            self.populate_list()
        else:
            self.populate_grid()

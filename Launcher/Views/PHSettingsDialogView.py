# Launcher/Views/PHSettingsDialogView.py
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QDialogButtonBox, QFileDialog, QComboBox
)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 450)

        # Path to config.ini
        self.config_path = Path(__file__).parents[2] / 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        # Main layout
        layout = QVBoxLayout(self)

        # Emulator Path
        emu_layout = QHBoxLayout()
        emu_layout.addWidget(QLabel("Emulator Path:"))
        self.emu_edit = QLineEdit()
        emu_layout.addWidget(self.emu_edit)
        emu_browse = QPushButton("Browse...")
        emu_browse.clicked.connect(self.browse_emulator)
        emu_layout.addWidget(emu_browse)
        layout.addLayout(emu_layout)

        # Scan Folders
        layout.addWidget(QLabel("Scan Folders:"))
        self.folder_list = QListWidget()
        layout.addWidget(self.folder_list)
        folder_btn_layout = QHBoxLayout()
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        remove_folder_btn = QPushButton("Remove Selected")
        remove_folder_btn.clicked.connect(self.remove_folder)
        folder_btn_layout.addWidget(add_folder_btn)
        folder_btn_layout.addWidget(remove_folder_btn)
        layout.addLayout(folder_btn_layout)

        # Theme Selector
        layout.addWidget(QLabel("Theme:"))
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System Default", "Light", "Dark", "Xbox 360", "Lavender Teal"])
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Dialog Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_settings()

    def load_settings(self):
        # Load emulator path
        emu_path = self.config.get('paths', 'xenia_path', fallback='')
        self.emu_edit.setText(emu_path)

        # Load scan folders
        self.folder_list.clear()
        folders = self.config.get('library', 'scan_folders', fallback='').split(';')
        for f in folders:
            if f:
                self.folder_list.addItem(f)

        # Load theme
        theme = self.config.get('appearance', 'theme', fallback='System Default')
        idx = self.theme_combo.findText(theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

    def browse_emulator(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Emulator Executable", "",
            "Executable Files (*.exe);;All Files (*)"
        )
        if path:
            self.emu_edit.setText(path)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Scan Folder", ""
        )
        if folder:
            self.folder_list.addItem(folder)

    def remove_folder(self):
        for item in self.folder_list.selectedItems():
            self.folder_list.takeItem(self.folder_list.row(item))

    def save_settings(self):
        # Ensure sections exist
        if not self.config.has_section('paths'):
            self.config.add_section('paths')
        if not self.config.has_section('library'):
            self.config.add_section('library')
        if not self.config.has_section('appearance'):
            self.config.add_section('appearance')

        # Save emulator path
        self.config.set('paths', 'xenia_path', self.emu_edit.text())
        # Save scan folders
        scan_folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        self.config.set('library', 'scan_folders', ';'.join(scan_folders))
        # Save theme
        self.config.set('appearance', 'theme', self.theme_combo.currentText())

        # Write back to file
        with open(self.config_path, 'w') as cfgfile:
            self.config.write(cfgfile)

    def accept(self):
        self.save_settings()
        super().accept()
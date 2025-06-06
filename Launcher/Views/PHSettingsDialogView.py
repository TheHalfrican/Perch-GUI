# Launcher/Views/PHSettingsDialogView.py
from pathlib import Path
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QDialogButtonBox, QFileDialog, QComboBox, QTabWidget,
    QWidget, QCheckBox, QSpinBox, QGroupBox, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt
from Launcher.ViewModels.PHSettingsDialogViewModel import SettingsDialogViewModel
import configparser
from Launcher.Utils.Utils import get_user_config_path

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Instantiate settings view model
        self.vm = SettingsDialogViewModel()
        self.setWindowTitle("Settings")
        self.resize(500, 450)
        # Ensure sufficient height on Windows so buttons are visible
        self.setMinimumSize(500, 600)

        # Create tab widget
        self.tabs = QTabWidget(self)

        # First tab: Basic Settings
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        # Emulator Path
        emu_layout = QHBoxLayout()
        emu_layout.addWidget(QLabel("Emulator Path:"))
        self.emu_edit = QLineEdit()
        emu_layout.addWidget(self.emu_edit)
        emu_browse = QPushButton("Browse...")
        emu_browse.clicked.connect(self.browse_emulator)
        emu_layout.addWidget(emu_browse)
        basic_layout.addLayout(emu_layout)

        # Scan Folders
        basic_layout.addWidget(QLabel("Scan Folders:"))
        self.folder_list = QListWidget()
        basic_layout.addWidget(self.folder_list)
        folder_btn_layout = QHBoxLayout()
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        remove_folder_btn = QPushButton("Remove Selected")
        remove_folder_btn.clicked.connect(self.remove_folder)
        folder_btn_layout.addWidget(add_folder_btn)
        folder_btn_layout.addWidget(remove_folder_btn)
        basic_layout.addLayout(folder_btn_layout)

        # Theme Selector
        basic_layout.addWidget(QLabel("Theme:"))
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System Default", "Light", "Dark", "Xbox 360", "Lavender Teal", "Custom"])
        theme_layout.addWidget(self.theme_combo)
        basic_layout.addLayout(theme_layout)

        # Custom Theme
        self.edit_custom_btn = QPushButton("Edit Custom Theme…")
        self.edit_custom_btn.setEnabled(False)
        self.edit_custom_btn.clicked.connect(self.open_custom_theme_editor)
        basic_layout.addWidget(self.edit_custom_btn)

        # Then hook up a signal so it only enables for “Custom”
        self.theme_combo.currentTextChanged.connect(
            lambda text: self.edit_custom_btn.setEnabled(text == "Custom")
        )
        # Add basic tab to tabs
        self.tabs.addTab(basic_tab, "General")

        # Second tab: Emulator Settings
        emu_tab = QWidget()
        emu_layout_tab = QVBoxLayout(emu_tab)
        emu_layout_tab.addWidget(QLabel("Xenia Canary Emulator Settings"))

        # ─── 1. Master Section ────────────────────────────────────────────────
        master_box = QGroupBox("General (Master)")
        master_layout = QFormLayout(master_box)
        master_layout.setLabelAlignment(Qt.AlignLeft)
        master_layout.setFormAlignment(Qt.AlignTop)

        # license_mask: Deactivated (0) vs. Activated (1)
        self.license_combo = QComboBox()
        self.license_combo.addItems(["Deactivated (0)", "Activated (1)"])
        master_layout.addRow("License Mode:", self.license_combo)

        # user_language: a few common codes
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "English (1)", "Japanese (2)", "German (3)", "French (4)",
            "Spanish (5)", "Italian (6)", "Korean (7)", "Chinese (8)"
        ])
        master_layout.addRow("User Language:", self.language_combo)

        # mount_cache: improves compatibility
        self.mount_cache_checkbox = QCheckBox("Mount Cache (improves compatibility)")
        master_layout.addRow("", self.mount_cache_checkbox)

        emu_layout_tab.addWidget(master_box)
        emu_layout_tab.addSpacing(10)

        # ─── 2. GPU Section ─────────────────────────────────────────────────
        gpu_box = QGroupBox("GPU / Renderer")
        gpu_layout = QFormLayout(gpu_box)
        gpu_layout.setLabelAlignment(Qt.AlignLeft)
        gpu_layout.setFormAlignment(Qt.AlignTop)

        # Renderer/Backend: “any”, “d3d12”, “vulkan”
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["any", "d3d12", "vulkan"])
        gpu_layout.addRow("Renderer / Backend:", self.renderer_combo)

        # Variable refresh (only relevant for D3D12)
        self.vsync_checkbox = QCheckBox("Allow Variable Refresh Rate & Tearing (d3d12)")
        gpu_layout.addRow("", self.vsync_checkbox)

        # Black bars: letterbox/pillarbox on mismatched aspect
        self.blackbars_checkbox = QCheckBox("Use Black Bars (letterbox/pillarbox)")
        gpu_layout.addRow("", self.blackbars_checkbox)

        emu_layout_tab.addWidget(gpu_box)
        emu_layout_tab.addSpacing(10)

        # ─── 3. HID (Input) Section ──────────────────────────────────────────
        input_box = QGroupBox("Input (HID)")
        input_layout = QFormLayout(input_box)
        input_layout.setLabelAlignment(Qt.AlignLeft)
        input_layout.setFormAlignment(Qt.AlignTop)

        # Keyboard Mode: “XInput”, “Keyboard”, “RawInput”
        self.keyboard_mode_combo = QComboBox()
        self.keyboard_mode_combo.addItems(["XInput", "Keyboard", "RawInput"])
        input_layout.addRow("Keyboard Mode:", self.keyboard_mode_combo)

        # Assigned Keyboard Slot: “0”–“3”
        self.keyboard_slot_spin = QSpinBox()
        self.keyboard_slot_spin.setRange(0, 3)
        self.keyboard_slot_spin.setSuffix(" (Player Slot)")
        input_layout.addRow("Assigned Keyboard Slot:", self.keyboard_slot_spin)

        emu_layout_tab.addWidget(input_box)
        emu_layout_tab.addSpacing(10)

        # ─── 4. Hacks (General) Section ──────────────────────────────────────
        hacks_box = QGroupBox("General Hacks")
        hacks_layout = QFormLayout(hacks_box)
        hacks_layout.setLabelAlignment(Qt.AlignLeft)
        hacks_layout.setFormAlignment(Qt.AlignTop)

        # protect_zero: prevent null-pointer crashes
        self.protect_zero_checkbox = QCheckBox("Protect Zero (prevent null‐ptr crashes)")
        hacks_layout.addRow("", self.protect_zero_checkbox)

        # break_on_unimplemented_instruction: for debugging
        self.break_on_unimpl_checkbox = QCheckBox("Break on Unimplemented Instruction")
        hacks_layout.addRow("", self.break_on_unimpl_checkbox)

        emu_layout_tab.addWidget(hacks_box)
        emu_layout_tab.addSpacing(10)

        # ─── 5. Canary-Only Video Section ────────────────────────────────────
        canary_video_box = QGroupBox("Canary Video Settings")
        canary_video_layout = QFormLayout(canary_video_box)
        canary_video_layout.setLabelAlignment(Qt.AlignLeft)
        canary_video_layout.setFormAlignment(Qt.AlignTop)

        # Vsync FPS: “off”, “60”, “30”, “120”
        self.vsync_fps_combo = QComboBox()
        self.vsync_fps_combo.addItems(["off", "60", "30", "120"])
        canary_video_layout.addRow("Vsync FPS:", self.vsync_fps_combo)

        # Internal display resolution: “720p”, “1080p”, “1440p”, “4K”
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "1440p", "4K"])
        canary_video_layout.addRow("Internal Display Resolution:", self.resolution_combo)

        # avpack: video mode ID
        self.avpack_line = QLineEdit()
        self.avpack_line.setPlaceholderText("avpack (e.g. \"XX81169X\")")
        canary_video_layout.addRow("AVPack (video mode ID):", self.avpack_line)

        emu_layout_tab.addWidget(canary_video_box)
        emu_layout_tab.addSpacing(10)

        # ─── 6. Canary-Only Hacks Section ────────────────────────────────────
        canary_hacks_box = QGroupBox("Canary Hacks")
        canary_hacks_layout = QFormLayout(canary_hacks_box)
        canary_hacks_layout.setLabelAlignment(Qt.AlignLeft)
        canary_hacks_layout.setFormAlignment(Qt.AlignTop)

        # Max queued frames: integer 1–10
        self.max_queued_spin = QSpinBox()
        self.max_queued_spin.setRange(1, 10)
        self.max_queued_spin.setSuffix(" Frames")
        canary_hacks_layout.addRow("Max Queued Frames:", self.max_queued_spin)

        # Clear GPU cache button
        self.clear_gpu_button = QPushButton("Clear GPU Cache Now")
        canary_hacks_layout.addRow("", self.clear_gpu_button)

        # Reset to default emulator settings button
        self.reset_defaults_button = QPushButton("Reset to Default Emulator Settings")
        self.reset_defaults_button.clicked.connect(self.on_reset_defaults)
        canary_hacks_layout.addRow("", self.reset_defaults_button)

        emu_layout_tab.addWidget(canary_hacks_box)
        emu_layout_tab.addSpacing(10)

        # Wrap emulator settings in a scroll area so contents aren’t squished
        emu_scroll = QScrollArea()
        emu_scroll.setWidgetResizable(True)
        emu_scroll.setWidget(emu_tab)
        self.tabs.addTab(emu_scroll, "Emulator")

        # Main layout for dialog
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

        # Dialog Buttons at bottom
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.load_settings()

    def load_settings(self):
        """
        Load all settings from the user-writable INI file.
        """
        ini_path = get_user_config_path()
        config = configparser.ConfigParser()
        if ini_path.exists():
            config.read(str(ini_path))

        # --- Emulator Path ---
        emu_path = config.get("paths", "xenia_path", fallback="")
        self.emu_edit.setText(emu_path)

        # --- Scan Folders ---
        self.folder_list.clear()
        folders = config.get("library", "scan_folders", fallback="")
        for f in folders.split(";"):
            if f:
                self.folder_list.addItem(f)

        # --- Theme ---
        theme = config.get("appearance", "theme", fallback="System Default")
        idx = self.theme_combo.findText(theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        # --- Emulator Master ---
        license_mask = config.getint("emulator_master", "license_mask", fallback=0)
        self.license_combo.setCurrentIndex(license_mask)
        user_language = config.getint("emulator_master", "user_language", fallback=1)
        lang_label = next((label for label in [self.language_combo.itemText(i) for i in range(self.language_combo.count())]
                           if label.endswith(f"({user_language})")), "")
        if lang_label:
            self.language_combo.setCurrentIndex(self.language_combo.findText(lang_label))
        mount_cache = config.getboolean("emulator_master", "mount_cache", fallback=False)
        self.mount_cache_checkbox.setChecked(mount_cache)

        # --- GPU ---
        renderer = config.get("gpu", "renderer", fallback="any")
        idx_renderer = self.renderer_combo.findText(renderer)
        if idx_renderer >= 0:
            self.renderer_combo.setCurrentIndex(idx_renderer)
        allow_vr = config.getboolean("gpu", "allow_variable_refresh", fallback=False)
        self.vsync_checkbox.setChecked(allow_vr)
        black_bars = config.getboolean("gpu", "black_bars", fallback=False)
        self.blackbars_checkbox.setChecked(black_bars)

        # --- Input ---
        keyboard_mode = config.get("input", "keyboard_mode", fallback="XInput")
        idx_kb_mode = self.keyboard_mode_combo.findText(keyboard_mode)
        if idx_kb_mode >= 0:
            self.keyboard_mode_combo.setCurrentIndex(idx_kb_mode)
        keyboard_slot = config.getint("input", "keyboard_slot", fallback=0)
        self.keyboard_slot_spin.setValue(keyboard_slot)

        # --- Hacks ---
        protect_zero = config.getboolean("hacks", "protect_zero", fallback=False)
        self.protect_zero_checkbox.setChecked(protect_zero)
        break_unimpl = config.getboolean("hacks", "break_on_unimplemented", fallback=False)
        self.break_on_unimpl_checkbox.setChecked(break_unimpl)

        # --- Canary Video ---
        vsync_fps = config.get("canary_video", "vsync_fps", fallback="off")
        idx_vsync_fps = self.vsync_fps_combo.findText(vsync_fps)
        if idx_vsync_fps >= 0:
            self.vsync_fps_combo.setCurrentIndex(idx_vsync_fps)
        internal_res = config.get("canary_video", "internal_resolution", fallback="720p")
        idx_res = self.resolution_combo.findText(internal_res)
        if idx_res >= 0:
            self.resolution_combo.setCurrentIndex(idx_res)
        avpack = config.get("canary_video", "avpack", fallback="")
        self.avpack_line.setText(avpack)

        # --- Canary Hacks ---
        max_frames = config.getint("canary_hacks", "max_queued_frames", fallback=1)
        self.max_queued_spin.setValue(max_frames)

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
        # Update ViewModel with UI values
        self.vm.emulator_path = self.emu_edit.text()
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        self.vm.scan_folders = folders
        self.vm.theme = self.theme_combo.currentText()

        license_text = self.license_combo.currentText()
        license_val = int(license_text.split()[-1].strip("()"))
        self.vm.license_mask = license_val

        language_text = self.language_combo.currentText()
        lang_val = int(language_text.split()[-1].strip("()"))
        self.vm.user_language = lang_val
        self.vm.mount_cache = self.mount_cache_checkbox.isChecked()

        self.vm.renderer = self.renderer_combo.currentText()
        self.vm.allow_variable_refresh = self.vsync_checkbox.isChecked()
        self.vm.black_bars = self.blackbars_checkbox.isChecked()

        self.vm.keyboard_mode = self.keyboard_mode_combo.currentText()
        self.vm.keyboard_slot = self.keyboard_slot_spin.value()

        self.vm.protect_zero = self.protect_zero_checkbox.isChecked()
        self.vm.break_on_unimplemented = self.break_on_unimpl_checkbox.isChecked()

        self.vm.vsync_fps = self.vsync_fps_combo.currentText()
        self.vm.internal_resolution = self.resolution_combo.currentText()
        self.vm.avpack = self.avpack_line.text()

        self.vm.max_queued_frames = self.max_queued_spin.value()

        # Now write all settings to the INI
        ini_path = get_user_config_path()
        config = configparser.ConfigParser()
        # If file exists, load existing to preserve unrelated sections
        if ini_path.exists():
            config.read(str(ini_path))

        # General section
        config['paths'] = {
            'xenia_path': self.vm.emulator_path
        }
        config['library'] = {
            'scan_folders': ";".join(self.vm.scan_folders)
        }
        config['appearance'] = {
            'theme': self.vm.theme
        }

        # Emulator Master section
        config['emulator_master'] = {
            'license_mask': str(self.vm.license_mask),
            'user_language': str(self.vm.user_language),
            'mount_cache': str(self.vm.mount_cache)
        }

        # GPU section
        config['gpu'] = {
            'renderer': self.vm.renderer,
            'allow_variable_refresh': str(self.vm.allow_variable_refresh),
            'black_bars': str(self.vm.black_bars)
        }

        # Input section
        config['input'] = {
            'keyboard_mode': self.vm.keyboard_mode,
            'keyboard_slot': str(self.vm.keyboard_slot)
        }

        # Hacks section
        config['hacks'] = {
            'protect_zero': str(self.vm.protect_zero),
            'break_on_unimplemented': str(self.vm.break_on_unimplemented)
        }

        # Canary Video section
        config['canary_video'] = {
            'vsync_fps': self.vm.vsync_fps,
            'internal_resolution': self.vm.internal_resolution,
            'avpack': self.vm.avpack
        }

        # Canary Hacks section
        config['canary_hacks'] = {
            'max_queued_frames': str(self.vm.max_queued_frames)
        }

        # Write back to the INI file
        with open(ini_path, 'w') as f:
            config.write(f)

    def accept(self):
        self.save_settings()
        super().accept()
    def on_reset_defaults(self):
        # Reset only emulator-specific settings
        self.vm.reset_emulator_settings()
        self.load_settings()

    def open_custom_theme_editor(self):
        from Launcher.Views.PHCustomThemeEditorView import CustomThemeEditorDialog
        dlg = CustomThemeEditorDialog(self, self.vm)
        dlg.exec()
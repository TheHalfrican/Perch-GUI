# Launcher/Views/PHGamepadConfigView.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox
)
from PySide6.QtCore import Qt
from Launcher.ViewModels.PHSettingsDialogViewModel import SettingsDialogViewModel
import configparser
from Launcher.Utils.Utils import get_user_config_path

class GamepadConfigView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = SettingsDialogViewModel()
        self.setWindowTitle("Controller Settings")
        self.resize(400, 200)

        # Main layout
        layout = QVBoxLayout(self)

        # Input (HID) section using FormLayout
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        # Keyboard Mode
        self.keyboard_mode_combo = QComboBox()
        self.keyboard_mode_combo.addItems(["XInput", "Keyboard", "RawInput"])
        form.addRow("Keyboard Mode:", self.keyboard_mode_combo)

        # Keyboard Slot
        self.keyboard_slot_spin = QSpinBox()
        self.keyboard_slot_spin.setRange(0, 3)
        self.keyboard_slot_spin.setSuffix(" (Player Slot)")
        form.addRow("Keyboard Slot:", self.keyboard_slot_spin)

        layout.addLayout(form)

        # Dialog Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_settings()

    def load_settings(self):
        """
        Load controller settings from the user-writable INI file.
        """
        ini_path = get_user_config_path()
        config = configparser.ConfigParser()
        if ini_path.exists():
            config.read(str(ini_path))

        # Keyboard Mode
        keyboard_mode = config.get("input", "keyboard_mode", fallback="XInput")
        idx_kb_mode = self.keyboard_mode_combo.findText(keyboard_mode)
        if idx_kb_mode >= 0:
            self.keyboard_mode_combo.setCurrentIndex(idx_kb_mode)

        # Keyboard Slot
        keyboard_slot = config.getint("input", "keyboard_slot", fallback=0)
        self.keyboard_slot_spin.setValue(keyboard_slot)

    def save_settings(self):
        """
        Save controller settings back to the INI file.
        """
        ini_path = get_user_config_path()
        config = configparser.ConfigParser()
        if ini_path.exists():
            config.read(str(ini_path))

        # Ensure sections exist
        if not config.has_section("input"):
            config.add_section("input")

        config.set("input", "keyboard_mode", self.keyboard_mode_combo.currentText())
        config.set("input", "keyboard_slot", str(self.keyboard_slot_spin.value()))

        with open(ini_path, 'w') as f:
            config.write(f)

    def accept(self):
        self.save_settings()
        super().accept()
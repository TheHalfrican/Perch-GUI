# Launcher/Views/PHGamepadConfigView.py
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox, QDialogButtonBox
)
from PySide6.QtCore import Qt
from Launcher.ViewModels.PHSettingsDialogViewModel import SettingsDialogViewModel

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
        # Load from ViewModel
        idx_kb_mode = self.keyboard_mode_combo.findText(self.vm.keyboard_mode)
        if idx_kb_mode >= 0:
            self.keyboard_mode_combo.setCurrentIndex(idx_kb_mode)
        self.keyboard_slot_spin.setValue(self.vm.keyboard_slot)

    def save_settings(self):
        # Write back to ViewModel
        self.vm.keyboard_mode = self.keyboard_mode_combo.currentText()
        self.vm.keyboard_slot = self.keyboard_slot_spin.value()

    def accept(self):
        self.save_settings()
        super().accept()
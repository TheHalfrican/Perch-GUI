# Launcher/Views/PHCustomThemeEditorView.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel,
    QPushButton, QColorDialog, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class CustomThemeEditorDialog(QDialog):
    def __init__(self, parent=None, vm=None):
        super().__init__(parent)
        self.vm = vm 
        self.setWindowTitle("Custom Theme Editor")
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        # 1) Background color
        self.bg_btn = QPushButton()
        self.bg_btn.setText("Choose Background Color")
        self.bg_btn.clicked.connect(self.choose_bg_color)
        form.addRow("Background:", self.bg_btn)

        # 2) Text color
        self.text_btn = QPushButton()
        self.text_btn.setText("Choose Text Color")
        self.text_btn.clicked.connect(self.choose_text_color)
        form.addRow("Text:", self.text_btn)

        # 3) Accent color
        self.accent_btn = QPushButton()
        self.accent_btn.setText("Choose Accent Color")
        self.accent_btn.clicked.connect(self.choose_accent_color)
        form.addRow("Accent:", self.accent_btn)

        layout.addLayout(form)

        # Dialog buttons
        from PySide6.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Load existing custom colors (if any)
        self.load_existing_colors()

    def load_existing_colors(self):
        """Populate button backgrounds with any previously saved custom colors."""
        # Fetch stored hex strings (e.g. "#1e1e1e") from VM; if empty, use defaults
        bg = self.vm.custom_bg_color or "#ffffff"
        txt = self.vm.custom_text_color or "#000000"
        accent = self.vm.custom_accent_color or "#0078d7"

        # Set button palettes so users see the current color
        self._set_button_color(self.bg_btn, QColor(bg))
        self._set_button_color(self.text_btn, QColor(txt))
        self._set_button_color(self.accent_btn, QColor(accent))

    def _set_button_color(self, btn: QPushButton, color: QColor):
        """Helper to colorize the button’s background so users see the current selection."""
        btn.setStyleSheet(f"background-color: {color.name()};")

    def choose_bg_color(self):
        initial = QColor(self.vm.custom_bg_color or "#ffffff")
        c = QColorDialog.getColor(initial, self, "Select Background Color")
        if c.isValid():
            self.vm.custom_bg_color = c.name()
            self._set_button_color(self.bg_btn, c)

    def choose_text_color(self):
        initial = QColor(self.vm.custom_text_color or "#000000")
        c = QColorDialog.getColor(initial, self, "Select Text Color")
        if c.isValid():
            self.vm.custom_text_color = c.name()
            self._set_button_color(self.text_btn, c)

    def choose_accent_color(self):
        initial = QColor(self.vm.custom_accent_color or "#0078d7")
        c = QColorDialog.getColor(initial, self, "Select Accent Color")
        if c.isValid():
            self.vm.custom_accent_color = c.name()
            self._set_button_color(self.accent_btn, c)

    def accept(self):
        """
        When user clicks OK, the VM properties (custom_bg_color, etc.) are already set.
        We just close; applying happens when Settings->OK is clicked.
        """
        super().accept()
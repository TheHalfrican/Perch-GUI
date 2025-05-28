import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)

label = QLabel("Hello from Perch GUI!")
label.show()

sys.exit(app.exec())
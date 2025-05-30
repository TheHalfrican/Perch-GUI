import sys
from PySide6.QtWidgets import QApplication
from Launcher.DB.PHDatabase import initialize_db
from Launcher.Views.PHMainWindowView import PerchLauncher

if __name__ == "__main__":
    initialize_db()
    app = QApplication(sys.argv)
    window = PerchLauncher()
    window.show()
    sys.exit(app.exec())
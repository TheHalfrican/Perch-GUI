import sys
from PySide6.QtWidgets import QApplication
from Launcher.DB.PHDatabase import initialize_db
from Launcher.Views.PHMainWindowView import MainWindowView

if __name__ == "__main__":
    initialize_db()
    app = QApplication(sys.argv)
    app.setApplicationName("Perch")
    app.setApplicationDisplayName("Perch")
    window = MainWindowView()
    window.show()
    sys.exit(app.exec())
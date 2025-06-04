import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from Launcher.DB.PHDatabase import initialize_db
from Launcher.Views.PHMainWindowView import MainWindowView

if __name__ == "__main__":
    initialize_db()
    app = QApplication(sys.argv)
    app.setApplicationName("Perch")
    app.setApplicationDisplayName("Perch")
    app.setWindowIcon(QIcon("Assets/app_icon.ico"))
    window = MainWindowView()
    window.setWindowIcon(QIcon("Assets/app_icon.ico"))
    window.show()
    sys.exit(app.exec())
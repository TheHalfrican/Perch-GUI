import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from Launcher.DB.PHDatabase import initialize_db
from Launcher.Utils.Utils import resource_path
from Launcher.Views.PHMainWindowView import MainWindowView

# Enable High-DPI scaling and high-DPI pixmap support via environment variables
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
os.environ['QT_ENABLE_HIGHDPI_BITMAP_SCALING'] = '1'

if __name__ == "__main__":
    initialize_db()
    app = QApplication(sys.argv)
    app.setApplicationName("Perch")
    app.setApplicationDisplayName("Perch")
    app.setWindowIcon(QIcon(resource_path('Assets/app_icon.ico')))
    window = MainWindowView()
    window.setWindowIcon(QIcon(resource_path('Assets/app_icon.ico')))
    window.show()
    sys.exit(app.exec())
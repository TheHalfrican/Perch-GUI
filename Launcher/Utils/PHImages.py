from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


def get_placeholder_pixmap(size: int = 100) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.lightGray)
    return pixmap
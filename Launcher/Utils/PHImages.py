from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt

def get_placeholder_pixmap(width: int = 300, height: int = 450) -> QPixmap:
    """Generate a placeholder pixmap with indigo background and instructional text with padding."""
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#4B0082"))  # Indigo background

    painter = QPainter(pixmap)
    painter.setPen(QColor("white"))
    font = QFont()
    font.setPointSize(int(min(width, height) / 12))
    font.setBold(True)
    painter.setFont(font)

    # Define padding bounds
    padding_x = int(width * 0.1)
    padding_y = int(height * 0.1)
    text_rect = pixmap.rect().adjusted(padding_x, padding_y, -padding_x, -padding_y)

    text = "Right-click to set\nCover Art"
    painter.drawText(text_rect, Qt.AlignCenter, text)
    painter.end()

    return pixmap
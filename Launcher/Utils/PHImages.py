from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt


def get_placeholder_pixmap(width: int = 300, height: int = 450, title: str | None = None) -> QPixmap:
    """Generate a placeholder pixmap with indigo background and optional title and instructional text with padding."""
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#4B0082"))  # Indigo background

    painter = QPainter(pixmap)
    painter.setPen(QColor("white"))

    # Padding
    padding_x = int(width * 0.1)
    padding_y = int(height * 0.1)

    if title:
        # Title font
        title_font = QFont()
        title_font.setPointSize(int(min(width, height) / 10))
        title_font.setBold(True)
        painter.setFont(title_font)
        title_rect = pixmap.rect().adjusted(padding_x, padding_y, -padding_x, -padding_y - height//2)
        painter.drawText(title_rect, Qt.AlignCenter, title)

        # Instruction font
        instr_font = QFont()
        instr_font.setPointSize(int(min(width, height) / 15))
        painter.setFont(instr_font)
        instr_text = "(Right-click to set Cover Art)"
        instr_rect = pixmap.rect().adjusted(padding_x, height//2, -padding_x, -padding_y)
        painter.drawText(instr_rect, Qt.AlignCenter, instr_text)
    else:
        # Default instruction only
        font = QFont()
        font.setPointSize(int(min(width, height) / 12))
        font.setBold(True)
        painter.setFont(font)
        text_rect = pixmap.rect().adjusted(padding_x, padding_y, -padding_x, -padding_y)
        painter.drawText(text_rect, Qt.AlignCenter, "Right-click to set\nCover Art")

    painter.end()
    return pixmap
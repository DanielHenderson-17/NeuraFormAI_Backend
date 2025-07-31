from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt


class PastChatContainer(QFrame):
    # === PastChatContainer for displaying past chat interactions in the left sidebar ===
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
            }
        """)

        # Prevent it from collapsing
        self.setMinimumWidth(100)

from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt


class PastChatContainer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QFrame {
                background-color: #121212;
                border: 2px dashed teal;
            }
        """)

        # Prevent it from collapsing
        self.setMinimumWidth(100)

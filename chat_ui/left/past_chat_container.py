from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

class PastChatContainer(QFrame):
    # === PastChatContainer for displaying past chat interactions in the left sidebar ===
    def __init__(self, parent=None):
        super().__init__(parent)

        # 🔧 Temporary background and border for testing
        self.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        # ✅ Prevent full width expansion
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(100)

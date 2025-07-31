from PyQt6.QtWidgets import QFrame, QSizePolicy
from PyQt6.QtCore import Qt


class VRMContainer(QFrame):
    # === VRMContainer for displaying VRM models in the center area ===
    def __init__(self, parent=None):
        super().__init__(parent)

        # ✅ Let it expand vertically
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )

        # Red debug border
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid red;
            }
        """)

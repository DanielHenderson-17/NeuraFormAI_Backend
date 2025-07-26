from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt


class ChatBubble(QWidget):
    def __init__(self, message, sender_name, align_right=False):
        super().__init__()
        self.message = message
        self.sender_name = sender_name
        self.align_right = align_right
        self.init_ui()

    def init_ui(self):
        bubble_bg = "#d1ecf1" if not self.align_right else "#ffffff"
        text_color = "#000000"

        full_text = f"{self.sender_name}: {self.message}"
        label = QLabel(full_text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # Add vertical padding and min height to support clean border-radius
        label.setStyleSheet(f"""
            background-color: {bubble_bg};
            color: {text_color};
            border: 1px solid #ccc;
            border-radius: 20px;
            padding: 16px 20px;
        """)
        label.setMinimumHeight(48)

        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Optional container to apply margins outside bubble
        frame = QWidget()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.addWidget(label)

        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Main layout to align bubble
        layout = QVBoxLayout(self)
        layout.addWidget(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight if self.align_right else Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(6, 6, 6, 6)

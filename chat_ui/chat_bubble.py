from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from datetime import datetime


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
        label.setStyleSheet(f"""
            background-color: {bubble_bg};
            color: {text_color};
            border: 1px solid #ccc;
            border-radius: 16px;
            padding: 12px 16px;
        """)
        label.setMinimumHeight(32)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Timestamp
        timestamp = QLabel(datetime.now().strftime("%I:%M %p").lstrip("0"))  # e.g., 2:41 PM
        timestamp.setStyleSheet("color: gray; font-size: 10px; margin-top: 4px;")
        timestamp.setAlignment(Qt.AlignmentFlag.AlignRight if self.align_right else Qt.AlignmentFlag.AlignLeft)

        # Bubble layout
        frame = QWidget()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(6, 6, 6, 6)  # tighter margins
        frame_layout.setSpacing(4)
        frame_layout.addWidget(label)
        frame_layout.addWidget(timestamp)

        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Main layout to align the whole thing
        layout = QVBoxLayout(self)
        layout.addWidget(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight if self.align_right else Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

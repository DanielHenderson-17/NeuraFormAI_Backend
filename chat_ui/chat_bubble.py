from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from datetime import datetime


class ChatBubble(QWidget):
    def __init__(self, message, sender_name, align_right=False):
        super().__init__()
        self.message = message                  # 🧾 The actual text of the message
        self.sender_name = sender_name          # 🧑 Name to prefix the message with
        self.align_right = align_right          # ⬅️➡️ Determines if the bubble is left or right aligned
        self.init_ui()                          # 🎨 Build the visual layout

    def init_ui(self):
        # 🎨 Bubble background color based on alignment
        bubble_bg = "#ffffff" if self.align_right else "#d1ecf1"
        text_color = "#000000"

        # 📋 QLabel displaying the sender and message
        label = QLabel(f"{self.sender_name}: {self.message}")
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

        # 🕒 Timestamp label (e.g., "3:45 PM")
        timestamp = QLabel(datetime.now().strftime("%I:%M %p").lstrip("0"))
        timestamp.setStyleSheet("color: gray; font-size: 10px; margin-top: 4px;")
        timestamp.setAlignment(Qt.AlignmentFlag.AlignRight if self.align_right else Qt.AlignmentFlag.AlignLeft)

        # 🧱 Container for message + timestamp (stacked vertically)
        bubble_container = QWidget()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(6, 6, 6, 6)
        bubble_layout.setSpacing(4)
        bubble_layout.addWidget(label)
        bubble_layout.addWidget(timestamp)

        # 🔄 Responsive width, max 75% of parent or 800px
        bubble_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bubble_container.setMaximumWidth(int(self.parentWidget().width() * 0.75) if self.parentWidget() else 800)

        # 🧭 Final horizontal layout to control left/right alignment
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 2, 8, 2)

        if self.align_right:
            main_layout.addStretch()               # ⬅ Push bubble to the right
            main_layout.addWidget(bubble_container)
        else:
            main_layout.addWidget(bubble_container)  # ⬅ Push bubble to the left
            main_layout.addStretch()

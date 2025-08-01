from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from datetime import datetime
from chat_ui.components.CodeBlockWidget import CodeBlockWidget


class ChatBubble(QWidget):
    # === ChatBubble for displaying messages in the chat window ===
    def __init__(self, message, sender_name, align_right=False):
        super().__init__()
        self.message = message
        self.sender_name = sender_name
        self.align_right = align_right
        self.init_ui()

    # === Initialize the UI components of the chat bubble ===
    def init_ui(self):
        bubble_bg = "#ffffff" if self.align_right else "#d1ecf1"
        text_color = "#000000"

        # === Bubble Content Layout ===
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        content_layout.setContentsMargins(12, 12, 12, 12)

        parts = self.message.split("```")
        is_code = False

        for part in parts:
            if is_code:
                lines = part.strip().split("\n")
                first_line = lines[0].strip().lower() if lines else ""
                known_langs = {"python", "bash", "html", "js", "javascript", "css", "json"}

                if first_line in known_langs:
                    lang = first_line
                    code = "\n".join(lines[1:])
                else:
                    lang = "code"
                    code = part.strip()

                content_layout.addWidget(CodeBlockWidget(code, lang))
            else:
                if part.strip():
                    self.label = QLabel(part.strip())  # ✅ Removed sender name from message
                    self.label.setWordWrap(True)
                    self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                    self.label.setStyleSheet(f"""
                        background-color: {bubble_bg};
                        color: {text_color};
                        border: 1px solid #ccc;
                        border-radius: 16px;
                        padding: 12px 16px;
                    """)
                    self.label.setMinimumHeight(32)
                    self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                    content_layout.addWidget(self.label)
            is_code = not is_code

        # === Footer with name + timestamp ===
        footer = QLabel(f"{self.sender_name} • {datetime.now().strftime('%I:%M %p').lstrip('0')}")
        footer.setStyleSheet("color: gray; font-size: 10px; margin-top: 4px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight if self.align_right else Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(footer)

        # === Bubble container ===
        bubble_container = QWidget()
        bubble_container.setLayout(content_layout)
        bubble_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bubble_container.setMaximumWidth(
            int(self.parentWidget().width() * 0.75) if self.parentWidget() else 800
        )

        # === Main layout ===
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 2, 8, 2)
        if self.align_right:
            main_layout.addStretch()
            main_layout.addWidget(bubble_container)
        else:
            main_layout.addWidget(bubble_container)
            main_layout.addStretch()

    # === Update the message content dynamically ===
    def set_message(self, new_message):
        self.message = new_message
        if hasattr(self, "label") and self.label:
            self.label.setText(new_message)  # ✅ No sender name prefix

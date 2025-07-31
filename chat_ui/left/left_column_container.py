from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from chat_ui.left.past_chat_container import PastChatContainer
from chat_ui.left.user_container import UserContainer

class LeftColumnContainer(QWidget):
    # === LeftColumnContainer for managing the left sidebar layout ===
    def __init__(self, parent=None):
        super().__init__(parent)

        # Outer layout for full left column
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # === Middle container with padding ===
        middle_container = QFrame()
        middle_layout = QVBoxLayout(middle_container)
        middle_layout.setContentsMargins(0, 0, 100, 0)
        middle_layout.setSpacing(0)

        # Children
        self.past_chat = PastChatContainer()
        self.user_container = UserContainer()

        middle_layout.addWidget(self.past_chat, stretch=4)
        middle_layout.addWidget(self.user_container, stretch=1)

        # Debug colors
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        # Add middle container into left column
        outer_layout.addWidget(middle_container)

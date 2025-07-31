from PyQt6.QtWidgets import QWidget, QVBoxLayout
from chat_ui.left.past_chat_container import PastChatContainer
from chat_ui.left.user_container import UserContainer

class LeftColumnContainer(QWidget):
    # === LeftColumnContainer for managing the left sidebar layout ===
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.past_chat = PastChatContainer()
        self.user_container = UserContainer()

        layout.addWidget(self.past_chat, stretch=4)
        layout.addWidget(self.user_container, stretch=1) 

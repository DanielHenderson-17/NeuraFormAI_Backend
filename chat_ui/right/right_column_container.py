from PyQt6.QtWidgets import QWidget, QVBoxLayout
from chat_ui.right.chat_window import ChatWindow

class RightColumnContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.chat_window = ChatWindow()
        self.chat_window.setStyleSheet("background-color: #1e1e1e;")

        layout.addWidget(self.chat_window, stretch=1)

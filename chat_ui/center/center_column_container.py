from PyQt6.QtWidgets import QWidget, QVBoxLayout
from chat_ui.center.vrm_container import VRMContainer
from chat_ui.center.chat_input import ChatInput

class CenterColumnContainer(QWidget):
    # === CenterColumnContainer for managing the center area layout ===
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0) 
        layout.setSpacing(0)

        self.vrm_container = VRMContainer()
        self.vrm_container.setStyleSheet("background-color: #1e1e1e;")

        self.chat_input = ChatInput(None, parent=self)
        self.chat_input.setStyleSheet("background-color: #1e1e1e;")

        layout.addWidget(self.vrm_container, stretch=3)
        layout.addWidget(self.chat_input, stretch=1)

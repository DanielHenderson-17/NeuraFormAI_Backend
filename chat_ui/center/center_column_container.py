from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from chat_ui.center.vrm_container import VRMContainer
from chat_ui.center.chat_input import ChatInput

class CenterColumnContainer(QWidget):
    # === CenterColumnContainer for managing the center area layout ===
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        self.vrm_container = VRMContainer()
        self.vrm_container.setStyleSheet("background-color: #1e1e1e;")

        self.chat_input = ChatInput(None, parent=self)
        # Ensure the chat input container itself is transparent
        self.chat_input.setStyleSheet("background-color: transparent;")

        # Stretch the VRM container to take up more space
        layout.addWidget(self.vrm_container, stretch=3)
        layout.addWidget(self.chat_input, stretch=1)
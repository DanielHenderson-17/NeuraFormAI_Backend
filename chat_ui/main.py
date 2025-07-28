import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from chat_ui.chat_window import ChatWindow
from chat_ui.chat_input import ChatInput
from chat_ui.vrm_container import VRMContainer
from chat_ui.past_chat_container import PastChatContainer

# Add parent path for module resolution
sys.path.append(str(Path(__file__).resolve().parent.parent))

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("chat_ui/assets/neuraform_icon.png"))

    window = QMainWindow()
    window.setWindowTitle("NeuraForm - AI Chat")
    window.resize(1400, 700)

    main_widget = QWidget()
    layout = QGridLayout(main_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # === Left column (past chats, div1)
    past_chat = PastChatContainer()
    past_chat.setStyleSheet("background-color: #1e1e1e;")
    layout.addWidget(past_chat, 0, 0, 2, 1)  # spans 2 rows, col 0

    # === Center column (VRM container + chat input, div4 + div5)
    vrm_container = VRMContainer()
    vrm_container.setStyleSheet("background-color: #1e1e1e;")
    layout.addWidget(vrm_container, 0, 1)

    chat_input = ChatInput(None, parent=main_widget)
    chat_input.setStyleSheet("background-color: #1e1e1e;")
    layout.addWidget(chat_input, 1, 1, alignment=Qt.AlignmentFlag.AlignBottom)

    # === Right column (chat window, div2)
    chat_window = ChatWindow()
    chat_window.setStyleSheet("background-color: #1e1e1e;")
    layout.addWidget(chat_window, 0, 2, 2, 1)  # spans 2 rows, col 2

    # Wire up chat input
    chat_input.chat_window = chat_window
    chat_window.input_box = chat_input

    # ✅ Set 1:2:1 column proportions
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 2)
    layout.setColumnStretch(2, 1)

    # ✅ Set 3:1 row proportions (VRM:Input = 75%:25%)
    layout.setRowStretch(0, 3)
    layout.setRowStretch(1, 1)

    window.setCentralWidget(main_widget)
    window.move(app.primaryScreen().availableGeometry().center() - window.rect().center())
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLineEdit, QPushButton,
    QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QEvent, QCoreApplication
from chat_ui.chat_bubble import ChatBubble
from chat_ui.persona_loader import get_persona_name
import threading
import requests


class ReplyEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text):
        super().__init__(ReplyEvent.EVENT_TYPE)
        self.text = text


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.persona_name = get_persona_name()
        self.setWindowTitle("NeuraForm - AI Chat")

        # === Main layout ===
        self.layout = QVBoxLayout(self)

        # === Scroll area setup ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #eaeaea;")

        self.scroll_content = QFrame()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_area.setWidget(self.scroll_content)

        # === Intermediate container ===
        self.inner_container = QWidget()
        self.inner_container.setStyleSheet("background-color: transparent;")
        self.inner_layout = QVBoxLayout(self.inner_container)
        self.inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # === Add inner container to scroll content ===
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_content_layout.addWidget(self.inner_container)

        # === Use inner_layout as scroll_layout alias ===
        self.scroll_layout = self.inner_layout

        # === Input field and send button ===
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type a message...")
        self.entry.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_row = QHBoxLayout()
        input_row.addWidget(self.entry)
        input_row.addWidget(self.send_button)

        # === Assemble layout ===
        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(input_row)

    def add_bubble(self, message, sender="user"):
        print(f"Adding bubble — sender: {sender}, message: {message}")

        bubble = ChatBubble(
            message=message,
            sender_name="You" if sender == "user" else self.persona_name,
            align_right=(sender == "user")
        )
        self.scroll_layout.addWidget(bubble)
        print("Bubble count:", self.scroll_layout.count())

        QCoreApplication.processEvents()
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def send_message(self):
        message = self.entry.text().strip()
        if not message:
            return
        self.add_bubble(message, sender="user")
        self.entry.clear()
        threading.Thread(target=self.fetch_reply, args=(message,), daemon=True).start()

    def fetch_reply(self, message):
        try:
            response = requests.post(
                "http://localhost:8000/chat/",
                json={
                    "user_id": "demo-user",
                    "message": message,
                    "mode": "safe"
                }
            )
            if response.status_code == 200:
                reply_text = response.json().get("reply", "")
            else:
                reply_text = f"(Error {response.status_code})"
        except Exception as e:
            reply_text = f"(Request failed: {e})"

        print("AI reply:", reply_text)
        QCoreApplication.postEvent(self, ReplyEvent(reply_text))

    def event(self, event):
        if event.type() == ReplyEvent.EVENT_TYPE:
            self.add_bubble(event.text, sender="ai")
            return True
        return super().event(event)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
)
from PyQt6.QtCore import Qt, QEvent, QCoreApplication, QTimer
from chat_ui.chat_bubble import ChatBubble
from chat_ui.persona_loader import get_persona_name
from chat_ui.voice_recorder import VoiceRecorder
from chat_ui.components.VoicePlayer import VoicePlayer

import threading
import requests


class ReplyEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text):
        super().__init__(ReplyEvent.EVENT_TYPE)
        self.text = text


class UserInputEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text):
        super().__init__(UserInputEvent.EVENT_TYPE)
        self.text = text


class TypingEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self):
        super().__init__(TypingEvent.EVENT_TYPE)


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumWidth(100)

        self.persona_name = get_persona_name()
        self.setWindowTitle("NeuraForm - AI Chat")
        self.recorder = VoiceRecorder()
        self.voice_player = VoicePlayer()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 4px 0;
            }
            QScrollBar::handle:vertical {
                background: #888;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #aaa;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.scroll_content = QFrame()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_area.setWidget(self.scroll_content)

        self.inner_container = QWidget()
        self.inner_container.setStyleSheet("background-color: transparent;")
        self.inner_layout = QVBoxLayout(self.inner_container)
        self.inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_content_layout.addWidget(self.inner_container)
        self.scroll_layout = self.inner_layout

        self.typing_label = None
        self.typing_timer = None
        self.typing_dots = 0

        self.layout.addWidget(self.scroll_area)

        self.input_box = None  # Will be set externally

    def add_bubble(self, message, sender="user"):
        bubble = ChatBubble(
            message=message,
            sender_name="You" if sender == "user" else self.persona_name,
            align_right=(sender == "user")
        )
        self.scroll_layout.addWidget(bubble)
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def fetch_reply(self, message):
        QCoreApplication.postEvent(self, TypingEvent())

        voice_enabled = self.input_box.is_voice_enabled() if self.input_box else False 

        try:
            response = requests.post(
                "http://localhost:8000/chat/",
                json={
                    "user_id": "demo-user",
                    "message": message,
                    "mode": "safe",
                    "voice_enabled": voice_enabled
                }
            )
            if response.status_code == 200:
                reply_text = response.json().get("reply", "")
            else:
                reply_text = f"(Error {response.status_code})"
        except Exception as e:
            reply_text = f"(Request failed: {e})"

        if voice_enabled:
            def on_start():
                QCoreApplication.postEvent(self, ReplyEvent(reply_text))

            threading.Thread(
                target=self.voice_player.play_reply_from_backend,
                args=(reply_text,),
                kwargs={"voice_enabled": True, "on_start": on_start},
                daemon=True
            ).start()
        else:
            QCoreApplication.postEvent(self, ReplyEvent(reply_text))

    def event(self, event):
        if event.type() == ReplyEvent.EVENT_TYPE:
            print("[ReplyEvent] AI reply received:", event.text)
            self.remove_typing_bubble()
            self.add_bubble(event.text, sender="ai")
            return True

        elif event.type() == TypingEvent.EVENT_TYPE:
            self.insert_typing_bubble()
            return True

        elif event.type() == UserInputEvent.EVENT_TYPE:
            self.add_bubble(event.text, sender="user")
            threading.Thread(target=self.fetch_reply, args=(event.text,), daemon=True).start()
            return True

        return super().event(event)

    def insert_typing_bubble(self):
        if self.typing_label:
            return

        self.typing_label = QLabel(f"{self.persona_name} is thinking")
        self.typing_label.setStyleSheet("""
            color: gray;
            font-size: 14px;
            padding: 8px 12px;
            margin-left: 16px;
        """)
        self.scroll_layout.addWidget(self.typing_label)
        self.scroll_to_bottom()

        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.update_typing_ellipsis)
        self.typing_timer.start(500)

    def remove_typing_bubble(self):
        if self.typing_timer:
            self.typing_timer.stop()
            self.typing_timer = None
        if self.typing_label:
            self.scroll_layout.removeWidget(self.typing_label)
            self.typing_label.deleteLater()
            self.typing_label = None
        self.typing_dots = 0

    def update_typing_ellipsis(self):
        if not self.typing_label:
            return

        self.typing_dots = (self.typing_dots + 1) % 4
        dots = "." * self.typing_dots
        updated_message = f"{self.persona_name} is thinking{dots}"
        self.typing_label.setText(updated_message)
        self.scroll_to_bottom()

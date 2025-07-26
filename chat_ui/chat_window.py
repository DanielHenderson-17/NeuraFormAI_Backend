from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLineEdit, QPushButton,
    QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QEvent, QCoreApplication, QTimer, QSize
from PyQt6.QtGui import QIcon
from chat_ui.chat_bubble import ChatBubble
from chat_ui.persona_loader import get_persona_name
from chat_ui.voice_recorder import VoiceRecorder
import threading
import requests


# 🎯 Custom Event used to inject AI replies into the UI thread
class ReplyEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text):
        super().__init__(ReplyEvent.EVENT_TYPE)
        self.text = text


# 🎯 Custom Event used to inject user voice input as if it was typed
class UserInputEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text):
        super().__init__(UserInputEvent.EVENT_TYPE)
        self.text = text


# 🪟 ChatWindow — main UI container for chat interaction
class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.persona_name = get_persona_name()
        self.setWindowTitle("NeuraForm - AI Chat")
        self.recorder = VoiceRecorder()
        self.voice_mode = False

        self.layout = QVBoxLayout(self)

        # === 💬 Scroll Area for Messages ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #181818;")

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
        self.scroll_layout = self.inner_layout  # alias

        self.layout.addWidget(self.scroll_area)

        # === 🎙️ Input + Toggle Buttons ===
        self.input_row = QHBoxLayout()

        self.entry = QLineEdit()
        self.entry.setFixedHeight(40)
        self.entry.setPlaceholderText("Start typing...")
        self.entry.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.setFixedHeight(40)
        self.send_button.clicked.connect(self.send_message)

        # Mic & Keyboard Toggle Buttons
        self.mic_button = QPushButton()
        self.mic_button.setIcon(QIcon("chat_ui/assets/mic.svg"))
        self.mic_button.setIconSize(QSize(18, 18))
        self.mic_button.setFixedSize(40, 40)
        self.mic_button.setCheckable(True)
        self.mic_button.clicked.connect(lambda: self.set_input_mode("mic"))

        self.keyboard_button = QPushButton()
        self.keyboard_button.setIcon(QIcon("chat_ui/assets/keyboard.svg"))
        self.keyboard_button.setIconSize(QSize(18, 18))
        self.keyboard_button.setFixedSize(40, 40)
        self.keyboard_button.setCheckable(True)
        self.keyboard_button.clicked.connect(lambda: self.set_input_mode("keyboard"))

        toggle_style = """
            QPushButton {
                border: 1px solid transparent;
                border-radius: 6px;
                background-color: transparent;
            }
            QPushButton:checked {
                background-color: gray;
                border: 1px solid #ccc;
            }
        """
        self.mic_button.setStyleSheet(toggle_style)
        self.keyboard_button.setStyleSheet(toggle_style)

        # Final layout
        self.input_row.addWidget(self.mic_button)
        self.input_row.addWidget(self.keyboard_button)
        self.input_row.addWidget(self.entry)
        self.input_row.addWidget(self.send_button)

        self.layout.addLayout(self.input_row)

        # Default mode = keyboard
        self.set_input_mode("keyboard")

    # 🧩 Toggles between mic and keyboard modes
    def set_input_mode(self, mode):
        self.voice_mode = (mode == "mic")

        if self.voice_mode:
            self.entry.setPlaceholderText("Listening...")
            self.entry.setReadOnly(True)
            self.send_button.setEnabled(False)
            self.mic_button.setChecked(True)
            self.keyboard_button.setChecked(False)
            self.recorder.continuous_mode = True
            self.recorder.start_recording_async(
                self.voice_input_callback,
                on_status=self.update_status
            )
        else:
            self.recorder.stop()
            self.entry.setPlaceholderText("Start typing...")
            self.entry.setReadOnly(False)
            self.send_button.setEnabled(True)
            self.mic_button.setChecked(False)
            self.keyboard_button.setChecked(True)

    # 📡 Handles live status updates from VoiceRecorder
    def update_status(self, text):
        text_clean = text.lower().strip()
        print(f"📣 update_status received: {text_clean}")
        if "stopped" in text_clean:
            self.set_input_mode("keyboard")
        else:
            self.entry.setPlaceholderText(text)

    # 💬 Adds a new ChatBubble to the chat area
    def add_bubble(self, message, sender="user"):
        bubble = ChatBubble(
            message=message,
            sender_name="You" if sender == "user" else self.persona_name,
            align_right=(sender == "user")
        )
        self.scroll_layout.addWidget(bubble)
        QTimer.singleShot(50, self.scroll_to_bottom)

    # 🔽 Auto-scroll to bottom after new message
    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    # 📤 Send typed message to API and clear input
    def send_message(self):
        message = self.entry.text().strip()
        if not message:
            return
        self.add_bubble(message, sender="user")
        self.entry.clear()
        threading.Thread(target=self.fetch_reply, args=(message,), daemon=True).start()

    # 📥 Send POST request to backend and queue response
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

        QCoreApplication.postEvent(self, ReplyEvent(reply_text))

    # 🎯 Handle custom events like voice input or server replies
    def event(self, event):
        if event.type() == ReplyEvent.EVENT_TYPE:
            self.add_bubble(event.text, sender="ai")
            return True
        elif event.type() == UserInputEvent.EVENT_TYPE:
            self.add_bubble(event.text, sender="user")
            threading.Thread(target=self.fetch_reply, args=(event.text,), daemon=True).start()
            return True
        return super().event(event)

    # 🎤 VoiceRecorder callback → triggers fake user input event
    def voice_input_callback(self, transcript):
        QCoreApplication.postEvent(self, UserInputEvent(transcript))

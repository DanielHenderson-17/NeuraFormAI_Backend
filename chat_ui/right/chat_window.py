import sys
import os
import threading
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
)
from PyQt6.QtCore import QEvent, Qt, QCoreApplication, QTimer
from PyQt6.QtGui import QFont

# Add the parent directory to the path to import from chat_ui
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_ui.right.chat_bubble import ChatBubble
from chat_ui.services.persona_service import PersonaService, SessionManager
from chat_ui.voice_recorder import VoiceRecorder
from chat_ui.components.VoicePlayer import VoicePlayer

# === Emotion detection function ===
def detect_emotion(message):
    """Detect emotion from message content"""
    message_lower = message.lower()
    
    emotion_keywords = {
        'happy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', '😊', '😄', '😍', 'fantastic', 'awesome'],
        'angry': ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful', '😠', '😡', '🤬', 'upset', 'annoyed'],
        'relaxed': ['fun', 'funny', 'lol', 'haha', 'amusing', '😆', '😂', '🤣', 'hilarious', 'joke'],
        'sad': ['sad', 'sorry', 'sorrow', 'depressed', 'unfortunate', '😢', '😭', '😔', 'unfortunate', 'disappointed'],
        'Surprised': ['wow', 'omg', 'surprised', 'shocked', 'unexpected', '😲', '😱', '🤯', 'incredible', 'unbelievable']
    }
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return emotion
    
    return 'neutral'

# === VRM Expression Manager ===
class VRMExpressionManager:
    """Manages VRM expressions for the chat system"""
    
    def __init__(self):
        self.vrm_viewer = None
        self._find_vrm_viewer()
    
    def _find_vrm_viewer(self):
        """Find the VRM viewer in the application"""
        try:
            # Try to import and find the VRM viewer
            from center.vrm_webview import VRMWebView
            # This will be set when the main application creates the VRM viewer
            print("🎭 VRM Expression Manager initialized")
        except ImportError:
            print("⚠️ VRM viewer not available")
    
    def set_vrm_viewer(self, vrm_viewer):
        """Set the VRM viewer instance"""
        self.vrm_viewer = vrm_viewer
        print("🎭 VRM viewer connected to expression manager")
    
    def set_emotion(self, emotion):
        """Set emotional expression on VRM model"""
        if self.vrm_viewer:
            try:
                self.vrm_viewer.set_emotion(emotion)
                print(f"🎭 Set VRM emotion: {emotion}")
            except Exception as e:
                print(f"⚠️ Failed to set VRM emotion: {e}")
        else:
            print(f"🎭 Would set VRM emotion: {emotion} (viewer not connected)")
    
    def set_lip_sync(self, phoneme):
        """Set lip sync expression"""
        if self.vrm_viewer:
            try:
                self.vrm_viewer.set_lip_sync(phoneme)
            except Exception as e:
                print(f"⚠️ Failed to set lip sync: {e}")
    
    def clear_lip_sync(self):
        """Clear lip sync expressions"""
        if self.vrm_viewer:
            try:
                self.vrm_viewer.clear_lip_sync()
            except Exception as e:
                print(f"⚠️ Failed to clear lip sync: {e}")
    
    def reset_expressions(self):
        """Reset to neutral expression"""
        if self.vrm_viewer:
            try:
                self.vrm_viewer.reset_expressions()
            except Exception as e:
                print(f"⚠️ Failed to reset expressions: {e}")

# Global VRM expression manager
vrm_expression_manager = VRMExpressionManager()

# === Event classes ===
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

class AutoGreetingEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text):
        super().__init__(AutoGreetingEvent.EVENT_TYPE)
        self.text = text

class TypingEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self):
        super().__init__(TypingEvent.EVENT_TYPE)

class ChatWindow(QWidget):
    # === ChatWindow for displaying chat messages and handling input ===
    
    def __init__(self):
        super().__init__()
        self.persona_name = "Assistant"
        self.setWindowTitle("NeuraPal - AI Chat")
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

    # === Add a chat bubble to the window ===
    def add_bubble(self, message, sender="user"):
        print(f"💬 [ChatWindow] Adding bubble - Sender: {sender}, Persona: {self.persona_name}")
        bubble = ChatBubble(
            message=message,
            sender_name="You" if sender == "user" else self.persona_name,
            align_right=(sender == "user")
        )
        self.scroll_layout.addWidget(bubble)
        QTimer.singleShot(50, self.scroll_to_bottom)

    # === Scroll to the bottom of the chat window ===
    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    # === Get the reply from the AI ===
    def fetch_reply(self, message):
        user_id = SessionManager.get_user_id()
        active_persona = PersonaService.get_active_persona()
        new_name = active_persona.get("name", "Assistant")
        if new_name != self.persona_name:
            print(f"🔄 [ChatWindow] Persona changed from {self.persona_name} → {new_name}")
            self.persona_name = new_name
    
        # Show typing bubble
        QCoreApplication.postEvent(self, TypingEvent())
    
        voice_enabled = self.input_box.is_voice_enabled() if self.input_box else False 
    
        print(f"🟢 [ChatWindow] Sending message for user_id={user_id}, Persona: {self.persona_name}")
    
        try:
            response = requests.post(
                "http://localhost:8000/chat/",
                json={
                    "user_id": user_id,
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
    
        print(f"🟢 [ChatWindow] Reply received: {reply_text}")
    
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

    # === Handle events ===
    def event(self, event):
        if event.type() == ReplyEvent.EVENT_TYPE:
            print("[ReplyEvent] AI reply displayed:", event.text)
            self.remove_typing_bubble()
            self.add_bubble(event.text, sender="ai")
            
            # 🎭 Detect emotion from AI response and set VRM expression
            ai_emotion = detect_emotion(event.text)
            if ai_emotion != 'neutral':
                print(f"🎭 Detected AI emotion: {ai_emotion}")
                vrm_expression_manager.set_emotion(ai_emotion)
            
            return True

        elif event.type() == TypingEvent.EVENT_TYPE:
            self.insert_typing_bubble()
            return True

        elif event.type() == UserInputEvent.EVENT_TYPE:
            print(f"🟢 [ChatWindow] User input event: {event.text}")
            self.add_bubble(event.text, sender="user")
            
            # 🎭 Detect emotion from user message and set VRM expression
            user_emotion = detect_emotion(event.text)
            if user_emotion != 'neutral':
                print(f"🎭 Detected user emotion: {user_emotion}")
                vrm_expression_manager.set_emotion(user_emotion)
            
            threading.Thread(target=self.fetch_reply, args=(event.text,), daemon=True).start()
            return True

        elif event.type() == AutoGreetingEvent.EVENT_TYPE:
            print(f"🟢 [ChatWindow] Auto-greeting triggered: {event.text}")
            threading.Thread(target=self.fetch_reply, args=(event.text,), daemon=True).start()
            return True

        return super().event(event)

    # === Insert a typing bubble ===
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

    # === Remove typing bubble ===
    def remove_typing_bubble(self):
        if self.typing_timer:
            self.typing_timer.stop()
            self.typing_timer = None
        if self.typing_label:
            self.scroll_layout.removeWidget(self.typing_label)
            self.typing_label.deleteLater()
            self.typing_label = None
        self.typing_dots = 0

    # === Update typing ellipsis ===
    def update_typing_ellipsis(self):
        if not self.typing_label:
            return

        self.typing_dots = (self.typing_dots + 1) % 4
        dots = "." * self.typing_dots
        updated_message = f"{self.persona_name} is thinking{dots}"
        self.typing_label.setText(updated_message)
        self.scroll_to_bottom()

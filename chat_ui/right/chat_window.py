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

# === Text to Phoneme Conversion ===
def text_to_phonemes(text):
    """Convert text to phonemes for lip-sync animation"""
    # Enhanced phoneme mapping for more natural speech
    phoneme_map = {
        'a': 'aa', 'e': 'ee', 'i': 'ih', 'o': 'oh', 'u': 'ou',
        'A': 'aa', 'E': 'ee', 'I': 'ih', 'O': 'oh', 'U': 'ou',
        'y': 'ih', 'Y': 'ih'
    }
    
    phonemes = []
    words = text.split()
    
    for word in words:
        word_lower = word.lower()
        word_phonemes = []
        
        # Find all vowels in the word for more detailed lip movement
        for vowel, phoneme in phoneme_map.items():
            if vowel in word_lower:
                word_phonemes.append(phoneme)
        
        if word_phonemes:
            # Use the most prominent vowel (usually the first one)
            phonemes.append(word_phonemes[0])
            # Add a brief neutral transition for longer words
            if len(word_phonemes) > 1:
                phonemes.append('ih')  # Brief closed mouth
        else:
            # If no vowel found, use neutral 'aa'
            phonemes.append('aa')
    
    return phonemes

# === Enhanced Emotion detection function ===
def detect_emotion(message):
    """Detect emotion from message content with semantic understanding"""
    message_lower = message.lower()
    
    # Direct emotion keywords (high confidence)
    emotion_keywords = {
        'happy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', '😊', '😄', '😍', 'fantastic', 'awesome'],
        'angry': ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful', '😠', '😡', '🤬', 'upset', 'annoyed'],
        'relaxed': ['fun', 'funny', 'lol', 'haha', 'amusing', '😆', '😂', '🤣', 'hilarious', 'joke'],
        'sad': ['sad', 'sorry', 'sorrow', 'depressed', 'unfortunate', '😢', '😭', '😔', 'unfortunate', 'disappointed'],
        'Surprised': ['wow', 'omg', 'surprised', 'shocked', 'unexpected', '😲', '😱', '🤯', 'incredible', 'unbelievable']
    }
    
    # Check direct emotion keywords first (highest priority)
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return emotion
    
    # Semantic emotion detection using word families and context
    def check_semantic_patterns(text):
        # Job stress and frustration patterns
        job_stress_patterns = [
            'quit', 'quitting', 'resign', 'resigning', 'leave', 'leaving',
            'burnout', 'burning out', 'burn out', 'burned out',
            'stress', 'stressed', 'stressing', 'overwhelmed', 'overwhelm',
            'exhausted', 'exhausting', 'tired of', 'sick of', 'fed up',
            'frustrated', 'frustrating', 'annoyed', 'annoying', 'pissed',
            'hate', 'hating', 'terrible', 'awful', 'horrible', 'worst',
            'unfair', 'wrong', 'stupid', 'idiot', 'dumb', 'ridiculous',
            'fire', 'fired', 'firing', 'layoff', 'laid off', 'terminated'
        ]
        
        # Loss and grief patterns
        loss_patterns = [
            'died', 'death', 'dead', 'lost', 'loss', 'miss', 'missing', 'gone',
            'passed away', 'passed', 'grandpa', 'grandma', 'father', 'mother',
            'sister', 'brother', 'friend', 'family', 'failed', 'failure',
            'broke', 'broken', 'lost job', 'fired', 'divorce', 'sick',
            'illness', 'cancer', 'hospital', 'pain', 'hurt', 'crying'
        ]
        
        # Success and achievement patterns
        success_patterns = [
            'got', 'received', 'won', 'success', 'achieved', 'accomplished',
            'graduated', 'promoted', 'new job', 'new house', 'engaged',
            'married', 'baby', 'pregnant', 'birthday', 'anniversary',
            'celebration', 'congratulations', 'amazing', 'incredible'
        ]
        
        # Surprise and shock patterns
        surprise_patterns = [
            'unexpected', 'shocking', 'unbelievable', 'incredible',
            'never thought', 'didn\'t expect', 'out of nowhere', 'suddenly',
            'just found out', 'discovered', 'wow', 'omg', 'oh my god'
        ]
        
        # Check each pattern family
        if any(pattern in text for pattern in job_stress_patterns):
            return 'angry'
        elif any(pattern in text for pattern in loss_patterns):
            return 'sad'
        elif any(pattern in text for pattern in success_patterns):
            return 'happy'
        elif any(pattern in text for pattern in surprise_patterns):
            return 'Surprised'
        
        return None
    
    # Try semantic detection
    semantic_result = check_semantic_patterns(message_lower)
    if semantic_result:
        return semantic_result
    
    # Additional context clues
    # Check for negative sentiment words that might indicate frustration
    negative_words = ['bad', 'worst', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'can\'t stand']
    if any(word in message_lower for word in negative_words):
        return 'angry'
    
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
    
    def set_emotion(self, emotion, duration=3.0):
        """Set emotional expression on VRM model and return to relaxed after duration seconds"""
        if self.vrm_viewer:
            try:
                self.vrm_viewer.set_emotion(emotion)
                print(f"🎭 Set VRM emotion: {emotion}")
                
                # Cancel any existing timer
                if hasattr(self, 'return_to_relaxed_timer') and self.return_to_relaxed_timer:
                    self.return_to_relaxed_timer.stop()
                
                # Set timer to return to relaxed expression
                self.return_to_relaxed_timer = QTimer()
                self.return_to_relaxed_timer.setSingleShot(True)
                self.return_to_relaxed_timer.timeout.connect(self._return_to_relaxed)
                self.return_to_relaxed_timer.start(int(duration * 1000))  # Convert to milliseconds
                
            except Exception as e:
                print(f"⚠️ Failed to set VRM emotion: {e}")
        else:
            print(f"🎭 Would set VRM emotion: {emotion} (viewer not connected)")
    
    def start_lip_sync(self, text, duration_per_word=0.15):
        """Start lip-sync animation for the given text"""
        if self.vrm_viewer:
            try:
                # Convert text to phonemes
                phonemes = text_to_phonemes(text)
                print(f"🎭 Starting lip-sync with {len(phonemes)} phonemes: {phonemes}")
                
                # Cancel any existing lip-sync
                self.stop_lip_sync()
                
                # Start lip-sync animation with faster, smoother timing
                self.lip_sync_phonemes = phonemes
                self.current_phoneme_index = 0
                self.lip_sync_timer = QTimer()
                self.lip_sync_timer.timeout.connect(self._next_phoneme)
                self.lip_sync_timer.start(int(duration_per_word * 1000))  # Convert to milliseconds
                
                # Start with first phoneme
                if phonemes:
                    self._set_current_phoneme()
                
            except Exception as e:
                print(f"⚠️ Failed to start lip-sync: {e}")
        else:
            print(f"🎭 Would start lip-sync (viewer not connected)")
    
    def stop_lip_sync(self):
        """Stop lip-sync animation"""
        if hasattr(self, 'lip_sync_timer') and self.lip_sync_timer:
            self.lip_sync_timer.stop()
            self.lip_sync_timer = None
        
        if hasattr(self, 'lip_sync_phonemes'):
            self.lip_sync_phonemes = None
            self.current_phoneme_index = 0
        
        # Clear lip-sync expressions
        self.clear_lip_sync()
    
    def _next_phoneme(self):
        """Move to next phoneme in lip-sync sequence"""
        if hasattr(self, 'lip_sync_phonemes') and self.lip_sync_phonemes:
            self.current_phoneme_index += 1
            
            if self.current_phoneme_index >= len(self.lip_sync_phonemes):
                # Lip-sync complete
                self.stop_lip_sync()
                print("🎭 Lip-sync animation complete")
            else:
                # Set next phoneme
                self._set_current_phoneme()
    
    def _set_current_phoneme(self):
        """Set the current phoneme expression"""
        if (hasattr(self, 'lip_sync_phonemes') and self.lip_sync_phonemes and 
            hasattr(self, 'current_phoneme_index') and 
            self.current_phoneme_index < len(self.lip_sync_phonemes)):
            
            phoneme = self.lip_sync_phonemes[self.current_phoneme_index]
            self.set_lip_sync(phoneme)
            print(f"🎭 Lip-sync phoneme {self.current_phoneme_index + 1}/{len(self.lip_sync_phonemes)}: {phoneme}")
    
    def _return_to_relaxed(self):
        """Return to relaxed expression (normal smile)"""
        if self.vrm_viewer:
            try:
                print("🎭 Returning to relaxed expression")
                self.vrm_viewer.set_emotion("relaxed")
            except Exception as e:
                print(f"⚠️ Failed to return to relaxed: {e}")
    
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
        self.last_user_emotion = 'neutral'  # Store the last user emotion

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
            
            # 🎭 Start lip-sync animation for AI response
            print(f"🎭 Starting lip-sync for AI response: {event.text[:50]}...")
            vrm_expression_manager.start_lip_sync(event.text, duration_per_word=0.12)
            
            # 🎭 Analyze AI response for emotional content and trigger appropriate expression
            ai_emotion = detect_emotion(event.text)
            if ai_emotion != 'neutral':
                print(f"🎭 AI response shows emotion: {ai_emotion}")
                vrm_expression_manager.set_emotion(ai_emotion)
            elif self.last_user_emotion != 'neutral':
                # If AI doesn't show emotion but user had emotion, AI should show empathy
                print(f"🎭 AI showing empathy for user emotion: {self.last_user_emotion}")
                vrm_expression_manager.set_emotion(self.last_user_emotion)
                self.last_user_emotion = 'neutral'  # Reset after triggering
            
            return True

        elif event.type() == TypingEvent.EVENT_TYPE:
            self.insert_typing_bubble()
            return True

        elif event.type() == UserInputEvent.EVENT_TYPE:
            print(f"🟢 [ChatWindow] User input event: {event.text}")
            self.add_bubble(event.text, sender="user")
            
            # 🎭 Detect and store emotion from user message (will trigger on AI response)
            self.last_user_emotion = detect_emotion(event.text)
            print(f"🎭 Emotion detection result: '{event.text}' → {self.last_user_emotion}")
            if self.last_user_emotion != 'neutral':
                print(f"🎭 Detected user emotion: {self.last_user_emotion} (will trigger on AI response)")
            
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

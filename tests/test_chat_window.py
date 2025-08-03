import pytest
from unittest.mock import MagicMock, patch, Mock
from PyQt6.QtWidgets import QApplication, QLabel, QScrollArea, QFrame, QWidget
from PyQt6.QtCore import QEvent, Qt, QTimer
from chat_ui.right.chat_window import (
    ChatWindow, TypingEvent, ReplyEvent, UserInputEvent, AutoGreetingEvent,
    text_to_phonemes, detect_emotion, VRMExpressionManager, vrm_expression_manager
)


class TestChatWindow:
    """Test cases for ChatWindow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication and mocks for each test"""
        self.app = QApplication(['test_app'])
        
        # Mock external dependencies
        with patch('chat_ui.right.chat_window.VoiceRecorder'), \
             patch('chat_ui.right.chat_window.VoicePlayer'), \
             patch('chat_ui.right.chat_window.PersonaService'), \
             patch('chat_ui.right.chat_window.SessionManager'):
            yield
        
        self.app.quit()
    
    @pytest.fixture
    def chat_window(self):
        """Create a ChatWindow instance"""
        with patch('chat_ui.right.chat_window.VoiceRecorder'), \
             patch('chat_ui.right.chat_window.VoicePlayer'), \
             patch('chat_ui.right.chat_window.PersonaService'), \
             patch('chat_ui.right.chat_window.SessionManager'):
            return ChatWindow()
    
    def test_init(self, chat_window):
        """Test ChatWindow initialization"""
        # Check basic properties
        assert chat_window.persona_name == "Assistant"
        assert chat_window.windowTitle() == "NeuraPal - AI Chat"
        assert chat_window.last_user_emotion == 'neutral'
        assert chat_window.input_box is None
        
        # Check layout structure - layout is a property, not a method
        main_layout = chat_window.layout
        assert main_layout is not None
        assert main_layout.count() == 1  # scroll_area
        
        # Check scroll area
        scroll_area = main_layout.itemAt(0).widget()
        assert isinstance(scroll_area, QScrollArea)
        assert scroll_area.widgetResizable()
        
        # Check scroll content structure
        scroll_content = scroll_area.widget()
        assert isinstance(scroll_content, QFrame)
        assert "background-color: transparent" in scroll_content.styleSheet()
        
        # Check inner container
        scroll_content_layout = scroll_content.layout()
        inner_container = scroll_content_layout.itemAt(0).widget()
        assert isinstance(inner_container, QWidget)
        
        # Check inner layout
        inner_layout = inner_container.layout()
        assert inner_layout is not None
        assert inner_layout.alignment() == Qt.AlignmentFlag.AlignTop
        
        # Check typing properties
        assert chat_window.typing_label is None
        assert chat_window.typing_timer is None
        assert chat_window.typing_dots == 0
    
    def test_add_bubble_user(self, chat_window):
        """Test adding user message bubble"""
        chat_window.add_bubble("Hello user", sender="user")
        
        # Check that bubble was added
        assert chat_window.scroll_layout.count() > 0
        
        # Get the last bubble
        bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
        assert bubble.message == "Hello user"
        assert bubble.sender_name == "You"
        assert bubble.align_right is True
    
    def test_add_bubble_ai(self, chat_window):
        """Test adding AI message bubble"""
        chat_window.add_bubble("Hello AI", sender="ai")
        
        # Check that bubble was added
        assert chat_window.scroll_layout.count() > 0
        
        # Get the last bubble
        bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
        assert bubble.message == "Hello AI"
        assert bubble.sender_name == "Assistant"
        assert bubble.align_right is False
    
    def test_add_bubble_custom_persona(self, chat_window):
        """Test adding AI message bubble with custom persona name"""
        chat_window.persona_name = "CustomBot"
        chat_window.add_bubble("Hello", sender="ai")
        
        # Get the last bubble
        bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
        assert bubble.sender_name == "CustomBot"
    
    def test_scroll_to_bottom(self, chat_window):
        """Test scrolling to bottom"""
        # Add some content to make scrolling meaningful
        chat_window.add_bubble("Test message", sender="user")
        
        # Mock the scroll bar
        mock_scrollbar = MagicMock()
        chat_window.scroll_area.verticalScrollBar = MagicMock(return_value=mock_scrollbar)
        
        chat_window.scroll_to_bottom()
        
        # Check that setValue was called with maximum
        mock_scrollbar.setValue.assert_called_once_with(mock_scrollbar.maximum())
    
    def test_insert_typing_bubble(self, chat_window):
        """Test inserting typing bubble"""
        chat_window.insert_typing_bubble()
        
        # Check that typing label was created
        assert chat_window.typing_label is not None
        assert isinstance(chat_window.typing_label, QLabel)
        assert "Assistant is thinking" in chat_window.typing_label.text()
        
        # Check styling
        assert "color: gray" in chat_window.typing_label.styleSheet()
        assert "font-size: 14px" in chat_window.typing_label.styleSheet()
        
        # Check that timer was created
        assert chat_window.typing_timer is not None
        assert isinstance(chat_window.typing_timer, QTimer)
        
        # Check that label was added to layout
        assert chat_window.scroll_layout.count() > 0
        last_widget = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
        assert last_widget == chat_window.typing_label
    
    def test_insert_typing_bubble_custom_persona(self, chat_window):
        """Test inserting typing bubble with custom persona"""
        chat_window.persona_name = "CustomBot"
        chat_window.insert_typing_bubble()
        
        assert "CustomBot is thinking" in chat_window.typing_label.text()
    
    def test_insert_typing_bubble_already_exists(self, chat_window):
        """Test inserting typing bubble when one already exists"""
        chat_window.insert_typing_bubble()
        original_label = chat_window.typing_label
        
        # Try to insert again
        chat_window.insert_typing_bubble()
        
        # Should not create a new one
        assert chat_window.typing_label == original_label
    
    def test_remove_typing_bubble(self, chat_window):
        """Test removing typing bubble"""
        # Insert typing bubble first
        chat_window.insert_typing_bubble()
        assert chat_window.typing_label is not None
        assert chat_window.typing_timer is not None
        
        # Remove it
        chat_window.remove_typing_bubble()
        
        # Check that everything was cleaned up
        assert chat_window.typing_label is None
        assert chat_window.typing_timer is None
        assert chat_window.typing_dots == 0
    
    def test_remove_typing_bubble_none_exists(self, chat_window):
        """Test removing typing bubble when none exists"""
        # Should not raise any errors
        chat_window.remove_typing_bubble()
        
        assert chat_window.typing_label is None
        assert chat_window.typing_timer is None
        assert chat_window.typing_dots == 0
    
    def test_update_typing_ellipsis(self, chat_window):
        """Test updating typing ellipsis"""
        chat_window.insert_typing_bubble()
        original_text = chat_window.typing_label.text()
        
        # Update ellipsis
        chat_window.update_typing_ellipsis()
        
        # Text should have changed
        assert chat_window.typing_label.text() != original_text
        assert chat_window.typing_dots == 1
    
    def test_update_typing_ellipsis_no_label(self, chat_window):
        """Test updating typing ellipsis when no label exists"""
        # Should not raise any errors
        chat_window.update_typing_ellipsis()
    
    def test_typing_event(self, chat_window):
        """Test TypingEvent handling"""
        event = TypingEvent()
        result = chat_window.event(event)
        
        assert result is True
        assert chat_window.typing_label is not None
    
    def test_reply_event_text_mode(self, chat_window):
        """Test ReplyEvent handling in text mode"""
        with patch.object(vrm_expression_manager, 'start_lip_sync') as mock_lip_sync, \
             patch.object(vrm_expression_manager, 'set_emotion') as mock_emotion:
            
            event = ReplyEvent("AI response")
            result = chat_window.event(event)
            
            assert result is True
            
            # Check that typing bubble was removed
            assert chat_window.typing_label is None
            
            # Check that bubble was added
            assert chat_window.scroll_layout.count() > 0
            bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
            assert bubble.message == "AI response"
            assert bubble.sender_name == "Assistant"
            assert bubble.align_right is False
            
            # Check that lip sync was started in text mode
            mock_lip_sync.assert_called_once_with("AI response", duration_per_word=0.08)
    
    def test_reply_event_voice_mode(self, chat_window):
        """Test ReplyEvent handling in voice mode"""
        with patch.object(vrm_expression_manager, 'start_lip_sync') as mock_lip_sync, \
             patch.object(vrm_expression_manager, 'set_emotion') as mock_emotion:
            
            event = ReplyEvent("AI response", audio_duration=5.0)
            result = chat_window.event(event)
            
            assert result is True
            
            # Check that lip sync was started in voice mode
            mock_lip_sync.assert_called_once_with("AI response", total_duration=5.0)
    
    def test_reply_event_with_emotion(self, chat_window):
        """Test ReplyEvent handling with emotion detection"""
        with patch.object(vrm_expression_manager, 'start_lip_sync'), \
             patch.object(vrm_expression_manager, 'set_emotion') as mock_emotion:
            
            event = ReplyEvent("I'm so happy today!")
            chat_window.event(event)
            
            # Check that emotion was detected and set
            mock_emotion.assert_called_once_with('happy')
    
    def test_reply_event_with_user_emotion_empathy(self, chat_window):
        """Test ReplyEvent handling with user emotion empathy"""
        with patch.object(vrm_expression_manager, 'start_lip_sync'), \
             patch.object(vrm_expression_manager, 'set_emotion') as mock_emotion:
            
            # Set user emotion
            chat_window.last_user_emotion = 'sad'
            
            event = ReplyEvent("Here's some information for you.")
            chat_window.event(event)
            
            # Check that AI showed empathy for user emotion
            mock_emotion.assert_called_once_with('sad')
            assert chat_window.last_user_emotion == 'neutral'  # Should be reset
    
    def test_user_input_event(self, chat_window):
        """Test UserInputEvent handling"""
        with patch('threading.Thread') as mock_thread, \
             patch.object(chat_window, 'fetch_reply') as mock_fetch:
            
            event = UserInputEvent("User message")
            result = chat_window.event(event)
            
            assert result is True
            
            # Check that bubble was added
            assert chat_window.scroll_layout.count() > 0
            bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
            assert bubble.message == "User message"
            assert bubble.sender_name == "You"
            assert bubble.align_right is True
            
            # Check that thread was started
            mock_thread.assert_called_once()
    
    def test_auto_greeting_event(self, chat_window):
        """Test AutoGreetingEvent handling"""
        with patch('threading.Thread') as mock_thread, \
             patch.object(chat_window, 'fetch_reply') as mock_fetch:
            
            event = AutoGreetingEvent("Greeting message")
            result = chat_window.event(event)
            
            assert result is True
            
            # Check that thread was started
            mock_thread.assert_called_once()
    
    def test_event_unknown_type(self, chat_window):
        """Test handling of unknown event type"""
        # Create a proper QEvent mock with unknown type
        class MockQEvent(QEvent):
            def __init__(self):
                super().__init__(QEvent.Type(99999))  # Unknown event type
        
        mock_event = MockQEvent()
        
        result = chat_window.event(mock_event)
        
        # Should return True (handled by parent class)
        assert result is True
    
    def test_fetch_reply_success(self, chat_window):
        """Test fetch_reply with successful response"""
        with patch('requests.post') as mock_post, \
             patch('chat_ui.right.chat_window.PersonaService.get_active_persona') as mock_get_persona, \
             patch('chat_ui.right.chat_window.SessionManager.get_user_id') as mock_get_user_id:
            
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"reply": "AI response"}
            mock_post.return_value = mock_response
            
            # Mock persona service
            mock_get_persona.return_value = {"name": "TestBot"}
            mock_get_user_id.return_value = "test_user"
            
            # Mock input box
            chat_window.input_box = MagicMock()
            chat_window.input_box.is_voice_enabled.return_value = False
            
            chat_window.fetch_reply("User message")
            
            # Check that persona name was updated
            assert chat_window.persona_name == "TestBot"
            
            # Check that request was made
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://localhost:8000/chat/"
            assert call_args[1]['json']['message'] == "User message"
            assert call_args[1]['json']['user_id'] == "test_user"
    
    def test_fetch_reply_error(self, chat_window):
        """Test fetch_reply with error response"""
        with patch('requests.post') as mock_post, \
             patch('chat_ui.right.chat_window.PersonaService.get_active_persona'), \
             patch('chat_ui.right.chat_window.SessionManager.get_user_id'):
            
            # Mock error response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response
            
            # Mock input box
            chat_window.input_box = MagicMock()
            chat_window.input_box.is_voice_enabled.return_value = False
            
            chat_window.fetch_reply("User message")
            
            # Should handle error gracefully
            mock_post.assert_called_once()
    
    def test_fetch_reply_exception(self, chat_window):
        """Test fetch_reply with exception"""
        with patch('requests.post', side_effect=Exception("Network error")), \
             patch('chat_ui.right.chat_window.PersonaService.get_active_persona'), \
             patch('chat_ui.right.chat_window.SessionManager.get_user_id'):
            
            # Mock input box
            chat_window.input_box = MagicMock()
            chat_window.input_box.is_voice_enabled.return_value = False
            
            chat_window.fetch_reply("User message")
            
            # Should handle exception gracefully
            pass  # No exception should be raised


class TestTextToPhonemes:
    """Test cases for text_to_phonemes function"""
    
    def test_text_to_phonemes_basic(self):
        """Test basic text to phonemes conversion"""
        result = text_to_phonemes("hello world")
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should contain phonemes
        expected_phonemes = ['aa', 'ee', 'ih', 'ou', 'oh']
        for phoneme in result:
            assert phoneme in expected_phonemes
    
    def test_text_to_phonemes_empty(self):
        """Test text to phonemes with empty string"""
        result = text_to_phonemes("")
        assert result == []
    
    def test_text_to_phonemes_no_vowels(self):
        """Test text to phonemes with no vowels"""
        result = text_to_phonemes("xyz")
        assert len(result) == 1
        assert result[0] == 'ih'  # Default phoneme for no vowels is 'ih', not 'aa'
    
    def test_text_to_phonemes_mixed_case(self):
        """Test text to phonemes with mixed case"""
        result = text_to_phonemes("Hello WORLD")
        assert isinstance(result, list)
        assert len(result) > 0


class TestDetectEmotion:
    """Test cases for detect_emotion function"""
    
    def test_detect_emotion_happy(self):
        """Test happy emotion detection"""
        assert detect_emotion("I'm so happy today!") == 'happy'
        assert detect_emotion("This is amazing!") == 'happy'
        assert detect_emotion("I love this!") == 'happy'
    
    def test_detect_emotion_sad(self):
        """Test sad emotion detection"""
        assert detect_emotion("I'm so sad") == 'sad'
        assert detect_emotion("This is unfortunate") == 'sad'
        assert detect_emotion("I miss you") == 'sad'
    
    def test_detect_emotion_angry(self):
        """Test angry emotion detection"""
        assert detect_emotion("I'm so angry!") == 'angry'
        assert detect_emotion("This is terrible") == 'angry'
        assert detect_emotion("I hate this") == 'angry'
    
    def test_detect_emotion_relaxed(self):
        """Test relaxed emotion detection"""
        assert detect_emotion("This is funny") == 'relaxed'
        assert detect_emotion("Haha that's hilarious") == 'relaxed'
        assert detect_emotion("LOL") == 'relaxed'
    
    def test_detect_emotion_surprised(self):
        """Test surprised emotion detection"""
        assert detect_emotion("Wow!") == 'Surprised'
        assert detect_emotion("OMG!") == 'Surprised'
        assert detect_emotion("This is incredible!") == 'Surprised'
    
    def test_detect_emotion_neutral(self):
        """Test neutral emotion detection"""
        assert detect_emotion("Hello there") == 'neutral'
        assert detect_emotion("How are you?") == 'neutral'
        assert detect_emotion("") == 'neutral'
    
    def test_detect_emotion_semantic_patterns(self):
        """Test semantic emotion detection patterns"""
        # Job stress patterns
        assert detect_emotion("I want to quit my job") == 'angry'
        assert detect_emotion("I'm so stressed at work") == 'angry'
        
        # Loss patterns
        assert detect_emotion("My grandfather died") == 'sad'
        assert detect_emotion("I lost my job") == 'sad'
        
        # Success patterns
        assert detect_emotion("I got promoted!") == 'happy'
        assert detect_emotion("I won the lottery") == 'happy'

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QTextEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
from chat_ui.right.chat_window import ChatWindow, UserInputEvent
import chat_ui.center.chat_input as chat_input_module
from chat_ui.center.chat_input import ChatInput, ChatInputTextEdit


class TestChatInput:
    """Test cases for ChatInput"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication and mock VoiceRecorder for each test"""
        self.app = QApplication(['test_app'])
        
        # Mock VoiceRecorder
        self.mock_voice_recorder = MagicMock()
        with patch.object(chat_input_module, 'VoiceRecorder', return_value=self.mock_voice_recorder):
            yield
        
        self.app.quit()
    
    @pytest.fixture
    def chat_window(self):
        """Create a mock chat window"""
        mock_window = MagicMock(spec=ChatWindow)
        # Add postEvent method to the mock
        mock_window.postEvent = MagicMock()
        return mock_window
    
    @pytest.fixture
    def chat_input(self, chat_window):
        """Create a ChatInput instance"""
        with patch.object(chat_input_module, 'VoiceRecorder', return_value=self.mock_voice_recorder):
            return ChatInput(chat_window=chat_window)
    
    def test_init(self, chat_input, chat_window):
        """Test ChatInput initialization"""
        # Check basic properties
        assert chat_input.chat_window == chat_window
        assert chat_input.voice_mode is False
        assert hasattr(chat_input, 'recorder')
        
        # Check styling
        assert "background-color: transparent" in chat_input.styleSheet()
        assert "border: 2px solid purple" in chat_input.styleSheet()
        
        # Check size policy
        size_policy = chat_input.sizePolicy()
        assert size_policy.horizontalPolicy() == chat_input.sizePolicy().Policy.Preferred
        assert size_policy.verticalPolicy() == chat_input.sizePolicy().Policy.Fixed
    
    def test_layout_structure(self, chat_input):
        """Test that the layout structure is correct"""
        # Check outer layout
        outer_layout = chat_input.layout()
        assert outer_layout is not None
        assert outer_layout.count() == 2  # toggle_container + bubble
        
        # Check toggle container
        toggle_container = outer_layout.itemAt(0).widget()
        assert toggle_container is not None
        
        # Check bubble
        bubble = outer_layout.itemAt(1).widget()
        assert isinstance(bubble, QFrame)
        assert "background-color: #333" in bubble.styleSheet()
        assert "border-radius: 12px" in bubble.styleSheet()
    
    def test_voice_toggle_creation(self, chat_input):
        """Test voice toggle switch creation"""
        assert hasattr(chat_input, 'voice_toggle')
        assert chat_input.voice_toggle is not None
        
        # Check that voice toggle is in toggle container
        outer_layout = chat_input.layout()
        toggle_container = outer_layout.itemAt(0).widget()
        toggle_layout = toggle_container.layout()
        assert toggle_layout.count() == 1  # voice toggle
    
    def test_text_entry_creation(self, chat_input):
        """Test text entry area creation"""
        assert hasattr(chat_input, 'entry')
        assert isinstance(chat_input.entry, ChatInputTextEdit)
        
        # Check placeholder text
        assert chat_input.entry.placeholderText() == "Start typing..."
        
        # Check styling
        entry_style = chat_input.entry.styleSheet()
        assert "background-color: #333" in entry_style
        assert "color: white" in entry_style
        assert "border: none" in entry_style
        
        # Check size constraints
        assert chat_input.entry.minimumHeight() == 44
        assert chat_input.entry.maximumHeight() == 44  # Set by adjust_textedit_height() during init
    
    def test_button_creation(self, chat_input):
        """Test button creation and properties"""
        # Check all buttons exist
        assert hasattr(chat_input, 'chat_toggle_button')
        assert hasattr(chat_input, 'mic_button')
        assert hasattr(chat_input, 'send_button')
        
        # Check button properties
        assert isinstance(chat_input.chat_toggle_button, QPushButton)
        assert isinstance(chat_input.mic_button, QPushButton)
        assert isinstance(chat_input.send_button, QPushButton)
        
        # Check button states
        assert chat_input.chat_toggle_button.isCheckable()
        assert chat_input.chat_toggle_button.isChecked()  # Should be checked by default
        assert chat_input.mic_button.isCheckable()
        assert not chat_input.mic_button.isChecked()  # Should not be checked by default
        assert not chat_input.send_button.isCheckable()  # Send button is not checkable
    
    def test_set_input_mode_keyboard(self, chat_input):
        """Test setting input mode to keyboard"""
        chat_input.set_input_mode("keyboard")
        
        assert chat_input.voice_mode is False
        assert chat_input.entry.placeholderText() == "Start typing..."
        assert chat_input.send_button.isEnabled()
        assert not chat_input.mic_button.isChecked()
        
        # Check that recorder was stopped
        self.mock_voice_recorder.stop.assert_called()
    
    def test_set_input_mode_mic(self, chat_input):
        """Test setting input mode to microphone"""
        chat_input.set_input_mode("mic")
        
        assert chat_input.voice_mode is True
        assert chat_input.entry.placeholderText() in ("Listening...", "Listening…")
        assert not chat_input.send_button.isEnabled()
        assert chat_input.mic_button.isChecked()
        
        # Check that recorder was started
        self.mock_voice_recorder.continuous_mode = True
        self.mock_voice_recorder.start_recording_async.assert_called_once()
    
    def test_send_message_empty(self, chat_input):
        """Test sending empty message"""
        chat_input.entry.setText("")
        chat_input.send_message()
        
        # Should not post event for empty message
        chat_input.chat_window.postEvent.assert_not_called()
    
    def test_send_message_normal(self, chat_input):
        """Test sending normal message"""
        test_message = "Hello world"
        chat_input.entry.setText(test_message)
        
        with patch('chat_ui.center.chat_input.QCoreApplication.postEvent') as mock_post_event:
            chat_input.send_message()
            
            # Check that text was cleared
            assert chat_input.entry.toPlainText() == ""
            
            # Check that event was posted
            mock_post_event.assert_called_once()
            event = mock_post_event.call_args[0][1]
            assert isinstance(event, UserInputEvent)
            assert event.text == test_message
    
    def test_send_message_persona_switch(self, chat_input):
        """Test persona switching via typed command"""
        with patch('chat_ui.center.chat_input.PersonaService.select_persona') as mock_select:
            chat_input.entry.setText("switch to fuka")
            chat_input.send_message()
            
            # Check that persona was selected
            mock_select.assert_called_once_with("fuka")
            
            # Check placeholder text was updated
            assert "Switched to fuka" in chat_input.entry.placeholderText()
    
    def test_send_message_persona_swap(self, chat_input):
        """Test persona switching with 'swap' command"""
        with patch('chat_ui.center.chat_input.PersonaService.select_persona') as mock_select:
            chat_input.entry.setText("swap to assistant")
            chat_input.send_message()
            
            # Check that persona was selected
            mock_select.assert_called_once_with("assistant")
    
    def test_toggle_chat_window(self, chat_input):
        """Test chat window visibility toggle"""
        # Mock chat window visibility
        chat_input.chat_window.isVisible.return_value = True
        
        # Toggle to hide
        chat_input.toggle_chat_window()
        chat_input.chat_window.setVisible.assert_called_with(False)
        assert not chat_input.chat_toggle_button.isChecked()
        
        # Reset mock
        chat_input.chat_window.setVisible.reset_mock()
        chat_input.chat_window.isVisible.return_value = False
        
        # Toggle to show
        chat_input.toggle_chat_window()
        chat_input.chat_window.setVisible.assert_called_with(True)
        assert chat_input.chat_toggle_button.isChecked()
    
    def test_toggle_mic(self, chat_input):
        """Test microphone toggle"""
        # Start in keyboard mode
        assert chat_input.voice_mode is False
        
        # Toggle to mic mode
        chat_input.toggle_mic()
        assert chat_input.voice_mode is True
        
        # Toggle back to keyboard mode
        chat_input.toggle_mic()
        assert chat_input.voice_mode is False
    
    def test_is_voice_enabled(self, chat_input):
        """Test voice enabled status"""
        # Mock voice toggle
        chat_input.voice_toggle.is_enabled = MagicMock(return_value=True)
        assert chat_input.is_voice_enabled() is True
        
        chat_input.voice_toggle.is_enabled.return_value = False
        assert chat_input.is_voice_enabled() is False
    
    def test_update_status(self, chat_input):
        """Test status update handling"""
        # Test stopped status
        chat_input.update_status("stopped")
        assert chat_input.voice_mode is False
        
        # Test listening status
        chat_input.update_status("listening")
        assert "Listening" in chat_input.entry.placeholderText()
        
        # Test other status
        chat_input.update_status("Processing...")
        assert chat_input.entry.placeholderText() == "Processing..."
    
    def test_voice_input_callback(self, chat_input):
        """Test voice input callback"""
        test_transcript = "Voice transcript"
        
        with patch('chat_ui.center.chat_input.QCoreApplication.postEvent') as mock_post_event:
            chat_input.voice_input_callback(test_transcript)
            
            # Check that event was posted
            mock_post_event.assert_called_once()
            event = mock_post_event.call_args[0][1]
            assert isinstance(event, UserInputEvent)
            assert event.text == test_transcript
    
    def test_send_greeting_message(self, chat_input):
        """Test sending greeting message"""
        with patch('builtins.print') as mock_print:
            with patch('chat_ui.center.chat_input.QCoreApplication.postEvent') as mock_post_event:
                chat_input.send_greeting_message()
                
                # Check that greeting was printed
                mock_print.assert_called_once()
                assert "Auto-sending greeting message" in mock_print.call_args[0][0]
                
                # Check that event was posted
                mock_post_event.assert_called_once()
                event = mock_post_event.call_args[0][1]
                assert isinstance(event, UserInputEvent)
                assert "Introduce yourself briefly" in event.text
    
    def test_adjust_textedit_height(self, chat_input):
        """Test text edit height adjustment"""
        # Set some text
        chat_input.entry.setText("Line 1\nLine 2\nLine 3")
        chat_input.adjust_textedit_height()
        
        # Height should be adjusted (we can't easily test exact values due to font metrics)
        assert chat_input.entry.height() >= 36
        assert chat_input.entry.height() <= 120


class TestChatInputTextEdit:
    """Test cases for ChatInputTextEdit"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication for each test"""
        self.app = QApplication(['test_app'])
        yield
        self.app.quit()
    
    def test_init(self):
        """Test ChatInputTextEdit initialization"""
        text_edit = ChatInputTextEdit()
        assert text_edit.send_callback is None
        
        # Test with callback
        callback = MagicMock()
        text_edit = ChatInputTextEdit(send_callback=callback)
        assert text_edit.send_callback == callback
    
    def test_key_press_enter_without_shift(self):
        """Test Enter key without Shift modifier"""
        callback = MagicMock()
        text_edit = ChatInputTextEdit(send_callback=callback)
        
        # Create Enter key event without Shift
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
        
        text_edit.keyPressEvent(event)
        callback.assert_called_once()
    
    def test_key_press_enter_with_shift(self):
        """Test Enter key with Shift modifier (should add newline)"""
        callback = MagicMock()
        text_edit = ChatInputTextEdit(send_callback=callback)
        
        # Create Enter key event with Shift
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.ShiftModifier)
        
        # Mock the parent keyPressEvent
        with patch.object(QTextEdit, 'keyPressEvent') as mock_parent:
            text_edit.keyPressEvent(event)
            mock_parent.assert_called_once_with(event)
            callback.assert_not_called()
    
    def test_key_press_other_key(self):
        """Test other key presses"""
        callback = MagicMock()
        text_edit = ChatInputTextEdit(send_callback=callback)
        
        # Create other key event
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.NoModifier)
        
        # Mock the parent keyPressEvent
        with patch.object(QTextEdit, 'keyPressEvent') as mock_parent:
            text_edit.keyPressEvent(event)
            mock_parent.assert_called_once_with(event)
            callback.assert_not_called()

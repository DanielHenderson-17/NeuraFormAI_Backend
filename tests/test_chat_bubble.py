import pytest
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt
from chat_ui.right.chat_bubble import ChatBubble
from chat_ui.components.CodeBlockWidget import CodeBlockWidget


class TestChatBubble:
    """Test cases for ChatBubble"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication for each test"""
        self.app = QApplication(['test_app'])
        yield
        self.app.quit()
    
    def test_init_left_aligned(self):
        """Test ChatBubble initialization with left alignment (AI messages)"""
        bubble = ChatBubble("Hello world", "Bot", align_right=False)
        
        # Check basic properties
        assert bubble.message == "Hello world"
        assert bubble.sender_name == "Bot"
        assert bubble.align_right is False
        
        # Check layout structure
        main_layout = bubble.layout()
        assert main_layout is not None
        assert main_layout.count() == 2  # bubble_container + stretch
        
        # Check that bubble container is first (left-aligned)
        bubble_container = main_layout.itemAt(0).widget()
        assert isinstance(bubble_container, QWidget)
    
    def test_init_right_aligned(self):
        """Test ChatBubble initialization with right alignment (user messages)"""
        bubble = ChatBubble("Hi there", "User", align_right=True)
        
        # Check basic properties
        assert bubble.message == "Hi there"
        assert bubble.sender_name == "User"
        assert bubble.align_right is True
        
        # Check layout structure
        main_layout = bubble.layout()
        assert main_layout is not None
        assert main_layout.count() == 2  # stretch + bubble_container
        
        # Check that stretch is first (right-aligned)
        bubble_container = main_layout.itemAt(1).widget()
        assert isinstance(bubble_container, QWidget)
    
    def test_simple_text_message(self):
        """Test ChatBubble with simple text message"""
        bubble = ChatBubble("Simple message", "TestUser", align_right=False)
        
        # Check that content layout has text label and footer
        main_layout = bubble.layout()
        bubble_container = main_layout.itemAt(0).widget()
        content_layout = bubble_container.layout()
        
        # Should have text label and footer (2 widgets)
        assert content_layout.count() == 2
        
        # Check text label
        text_label = content_layout.itemAt(0).widget()
        assert isinstance(text_label, QLabel)
        assert text_label.text() == "Simple message"
        assert text_label.wordWrap() is True
        assert text_label.textInteractionFlags() == Qt.TextInteractionFlag.TextSelectableByMouse
    
    def test_code_block_message(self):
        """Test ChatBubble with code block message"""
        message = "Here's some code:\n```python\ndef hello():\n    print('Hello')\n```"
        bubble = ChatBubble(message, "TestUser", align_right=False)
        
        # Check that content layout has text, code block, and footer
        main_layout = bubble.layout()
        bubble_container = main_layout.itemAt(0).widget()
        content_layout = bubble_container.layout()
        
        # Should have text label, code block widget, and footer (3 widgets)
        assert content_layout.count() == 3
        
        # Check text label
        text_label = content_layout.itemAt(0).widget()
        assert isinstance(text_label, QLabel)
        assert text_label.text() == "Here's some code:"
        
        # Check code block widget
        code_widget = content_layout.itemAt(1).widget()
        assert isinstance(code_widget, CodeBlockWidget)
    
    def test_footer_content(self):
        """Test that footer contains sender name and timestamp"""
        bubble = ChatBubble("Test message", "TestUser", align_right=False)
        
        main_layout = bubble.layout()
        bubble_container = main_layout.itemAt(0).widget()
        content_layout = bubble_container.layout()
        
        # Get footer (last widget)
        footer = content_layout.itemAt(content_layout.count() - 1).widget()
        assert isinstance(footer, QLabel)
        
        # Check footer content
        footer_text = footer.text()
        assert "TestUser" in footer_text
        assert "•" in footer_text  # Separator
        assert ":" in footer_text  # Time separator
    
    def test_footer_alignment(self):
        """Test footer alignment matches bubble alignment"""
        # Left aligned
        left_bubble = ChatBubble("Left message", "User", align_right=False)
        left_main_layout = left_bubble.layout()
        left_bubble_container = left_main_layout.itemAt(0).widget()
        left_content_layout = left_bubble_container.layout()
        left_footer = left_content_layout.itemAt(left_content_layout.count() - 1).widget()
        
        assert left_footer.alignment() == Qt.AlignmentFlag.AlignLeft
        
        # Right aligned
        right_bubble = ChatBubble("Right message", "User", align_right=True)
        right_main_layout = right_bubble.layout()
        right_bubble_container = right_main_layout.itemAt(1).widget()
        right_content_layout = right_bubble_container.layout()
        right_footer = right_content_layout.itemAt(right_content_layout.count() - 1).widget()
        
        assert right_footer.alignment() == Qt.AlignmentFlag.AlignRight
    
    def test_set_message_method(self):
        """Test set_message method updates the message content"""
        bubble = ChatBubble("Original message", "User", align_right=False)
        
        # Update message
        bubble.set_message("Updated message")
        
        # Check that message was updated
        assert bubble.message == "Updated message"
        
        # Check that label text was updated if label exists
        if hasattr(bubble, 'label') and bubble.label:
            assert bubble.label.text() == "Updated message"
    
    def test_empty_message(self):
        """Test ChatBubble with empty message"""
        bubble = ChatBubble("", "User", align_right=False)
        
        # Should still create the bubble structure
        assert bubble.message == ""
        assert bubble.sender_name == "User"
        
        # Layout should still be created
        main_layout = bubble.layout()
        assert main_layout is not None

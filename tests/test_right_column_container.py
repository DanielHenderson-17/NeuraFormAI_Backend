import pytest
from PyQt6.QtWidgets import QApplication
from chat_ui.right.right_column_container import RightColumnContainer
from chat_ui.right.chat_window import ChatWindow

class TestRightColumnContainer:
    """Test cases for RightColumnContainer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication for each test"""
        self.app = QApplication(['test_app'])
        yield
        self.app.quit()
    
    def test_init(self):
        """Test RightColumnContainer initialization"""
        container = RightColumnContainer()
        
        # Check that container is properly initialized
        assert container is not None
        assert isinstance(container, RightColumnContainer)
        
        # Check that chat window is created and added
        assert hasattr(container, 'chat_window')
        assert isinstance(container.chat_window, ChatWindow)
        
        # Check layout properties
        layout = container.layout()
        assert layout is not None
        assert layout.contentsMargins().left() == 0
        assert layout.contentsMargins().right() == 0
        assert layout.contentsMargins().top() == 0
        assert layout.contentsMargins().bottom() == 0
        assert layout.spacing() == 0
    
    def test_chat_window_style(self):
        """Test that chat window has correct styling"""
        container = RightColumnContainer()
        
        # Check that chat window has the expected background color
        expected_style = "background-color: #1e1e1e;"
        assert container.chat_window.styleSheet() == expected_style
    
    def test_layout_stretch(self):
        """Test that chat window is added with proper stretch"""
        container = RightColumnContainer()
        
        # Check that chat window is the only widget in layout
        layout = container.layout()
        assert layout.count() == 1
        
        # Check that the widget at index 0 is the chat window
        widget = layout.itemAt(0).widget()
        assert widget == container.chat_window 
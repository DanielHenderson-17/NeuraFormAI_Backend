import pytest
from PyQt6.QtWidgets import QApplication, QSizePolicy
from PyQt6.QtCore import Qt
from chat_ui.left.past_chat_container import PastChatContainer

class TestPastChatContainer:
    """Test cases for PastChatContainer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication for each test"""
        self.app = QApplication(['test_app'])
        yield
        self.app.quit()
    
    def test_init(self):
        """Test PastChatContainer initialization"""
        container = PastChatContainer()
        
        # Check that container is properly initialized
        assert container is not None
        assert isinstance(container, PastChatContainer)
        
        # Check layout properties
        layout = container.layout()
        assert layout is not None
        assert layout.contentsMargins().left() == 10
        assert layout.contentsMargins().right() == 10
        assert layout.contentsMargins().top() == 10
        assert layout.contentsMargins().bottom() == 10
        assert layout.spacing() == 0
    
    def test_container_style(self):
        """Test container styling"""
        container = PastChatContainer()
        
        # Check styling
        expected_style = """
            QFrame {
                background-color: #2c2c2c;
            }
        """
        assert container.styleSheet().strip() == expected_style.strip()
    
    def test_size_policy(self):
        """Test size policy settings"""
        container = PastChatContainer()
        
        # Check size policy
        size_policy = container.sizePolicy()
        assert size_policy.horizontalPolicy() == QSizePolicy.Policy.Preferred
        assert size_policy.verticalPolicy() == QSizePolicy.Policy.Expanding
    
    def test_minimum_width(self):
        """Test minimum width setting"""
        container = PastChatContainer()
        
        # Check minimum width
        assert container.minimumWidth() == 100 
import pytest
from PyQt6.QtWidgets import QApplication, QFrame
from chat_ui.left.left_column_container import LeftColumnContainer
from chat_ui.left.past_chat_container import PastChatContainer
from chat_ui.left.user_container import UserContainer

class TestLeftColumnContainer:
    """Test cases for LeftColumnContainer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication for each test"""
        self.app = QApplication(['test_app'])
        yield
        self.app.quit()
    
    def test_init(self):
        """Test LeftColumnContainer initialization"""
        container = LeftColumnContainer()
        
        # Check that container is properly initialized
        assert container is not None
        assert isinstance(container, LeftColumnContainer)
        
        # Check outer layout properties
        outer_layout = container.layout()
        assert outer_layout is not None
        assert outer_layout.contentsMargins().left() == 0
        assert outer_layout.contentsMargins().right() == 0
        assert outer_layout.contentsMargins().top() == 0
        assert outer_layout.contentsMargins().bottom() == 0
        assert outer_layout.spacing() == 0
    
    def test_container_style(self):
        """Test container styling"""
        container = LeftColumnContainer()
        
        # Check styling
        expected_style = """
            QWidget {
                background-color: transparent;
            }
        """
        assert container.styleSheet().strip() == expected_style.strip()
    
    def test_past_chat_container(self):
        """Test past chat container creation"""
        container = LeftColumnContainer()
        
        # Check that past chat container is created
        assert hasattr(container, 'past_chat')
        assert isinstance(container.past_chat, PastChatContainer)
    
    def test_user_container(self):
        """Test user container creation"""
        container = LeftColumnContainer()
        
        # Check that user container is created
        assert hasattr(container, 'user_container')
        assert isinstance(container.user_container, UserContainer)
    
    def test_middle_container_structure(self):
        """Test middle container structure and layout"""
        container = LeftColumnContainer()
        
        outer_layout = container.layout()
        
        # Check that there's exactly one widget in outer layout
        assert outer_layout.count() == 1
        
        # Get the middle container (should be a QFrame)
        middle_container = outer_layout.itemAt(0).widget()
        assert isinstance(middle_container, QFrame)
        
        # Check middle container layout
        middle_layout = middle_container.layout()
        assert middle_layout is not None
        assert middle_layout.contentsMargins().left() == 0
        assert middle_layout.contentsMargins().right() == 100
        assert middle_layout.contentsMargins().top() == 0
        assert middle_layout.contentsMargins().bottom() == 0
        assert middle_layout.spacing() == 0
        
        # Check that there are exactly 2 widgets in middle layout
        assert middle_layout.count() == 2
        
        # Check first widget (past chat)
        past_chat_item = middle_layout.itemAt(0)
        assert past_chat_item.widget() == container.past_chat
        
        # Check second widget (user container)
        user_item = middle_layout.itemAt(1)
        assert user_item.widget() == container.user_container 
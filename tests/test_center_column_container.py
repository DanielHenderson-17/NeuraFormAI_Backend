import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from chat_ui.center.center_column_container import CenterColumnContainer
from chat_ui.center.vrm_container import VRMContainer
from chat_ui.center.chat_input import ChatInput

class TestCenterColumnContainer:
    """Test cases for CenterColumnContainer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication for each test"""
        self.app = QApplication(['test_app'])
        yield
        self.app.quit()
    
    def test_init(self):
        """Test CenterColumnContainer initialization"""
        container = CenterColumnContainer()
        
        # Check that container is properly initialized
        assert container is not None
        assert isinstance(container, CenterColumnContainer)
        
        # Check layout properties
        layout = container.layout()
        assert layout is not None
        assert layout.contentsMargins().left() == 20
        assert layout.contentsMargins().right() == 20
        assert layout.contentsMargins().top() == 0
        assert layout.contentsMargins().bottom() == 0
        assert layout.spacing() == 0
    
    def test_container_attributes(self):
        """Test container styling and attributes"""
        container = CenterColumnContainer()
        
        # Check styling
        assert container.styleSheet() == "background-color: transparent;"
        
        # Check attributes
        assert container.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        assert not container.autoFillBackground()
    
    def test_vrm_container(self):
        """Test VRM container creation and styling"""
        container = CenterColumnContainer()
        
        # Check that VRM container is created
        assert hasattr(container, 'vrm_container')
        assert isinstance(container.vrm_container, VRMContainer)
        
        # Check VRM container styling
        expected_style = "background-color: #1e1e1e;"
        assert container.vrm_container.styleSheet() == expected_style
    
    def test_chat_input(self):
        """Test chat input creation and styling"""
        container = CenterColumnContainer()
        
        # Check that chat input is created
        assert hasattr(container, 'chat_input')
        assert isinstance(container.chat_input, ChatInput)
        
        # Check chat input styling
        expected_style = "background-color: transparent;"
        assert container.chat_input.styleSheet() == expected_style
    
    def test_layout_widgets(self):
        """Test that widgets are added to layout with correct stretch"""
        container = CenterColumnContainer()
        
        layout = container.layout()
        
        # Check that there are exactly 2 widgets
        assert layout.count() == 2
        
        # Check first widget (VRM container) with stretch 3
        vrm_item = layout.itemAt(0)
        assert vrm_item.widget() == container.vrm_container
        # Use layout's stretch method instead of item's stretch method
        assert layout.stretch(0) == 3
        
        # Check second widget (chat input) with stretch 1
        chat_item = layout.itemAt(1)
        assert chat_item.widget() == container.chat_input
        assert layout.stretch(1) == 1 
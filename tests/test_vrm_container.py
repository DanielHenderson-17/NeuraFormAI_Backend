import pytest
from PyQt6.QtWidgets import QApplication
from chat_ui.center.vrm_container import VRMContainer
from chat_ui.center.vrm_webview import VRMWebView

class TestVRMContainer:
    """Test cases for VRMContainer"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup QApplication for each test"""
        self.app = QApplication(['test_app'])
        yield
        self.app.quit()
    
    def test_init(self):
        """Test VRMContainer initialization"""
        container = VRMContainer()
        
        # Check that container is properly initialized
        assert container is not None
        assert isinstance(container, VRMContainer)
        
        # Check styling
        expected_style = "background-color: transparent; border: 2px solid red;"
        assert container.styleSheet() == expected_style
        
        # Check layout properties
        layout = container.layout()
        assert layout is not None
        assert layout.contentsMargins().left() == 0
        assert layout.contentsMargins().right() == 0
        assert layout.contentsMargins().top() == 0
        assert layout.contentsMargins().bottom() == 0
    
    def test_vrm_renderer_creation(self):
        """Test VRM renderer creation"""
        container = VRMContainer()
        
        # Check that VRM renderer is created
        assert hasattr(container, 'vrm_renderer')
        assert isinstance(container.vrm_renderer, VRMWebView)
        
        # Check that renderer is added to layout
        layout = container.layout()
        assert layout.count() == 1
        assert layout.itemAt(0).widget() == container.vrm_renderer
    
    def test_vrm_path_initialization(self):
        """Test VRM path initialization"""
        container = VRMContainer()
        
        # Check that vrm_path is initialized to None
        assert hasattr(container, 'vrm_path')
        assert container.vrm_path is None
    
    def test_load_vrm_method(self):
        """Test load_vrm method exists"""
        container = VRMContainer()
        
        # Check that load_vrm method exists
        assert hasattr(container, 'load_vrm')
        assert callable(container.load_vrm)
    
    def test_trigger_blink_method(self):
        """Test trigger_blink method exists"""
        container = VRMContainer()
        
        # Check that trigger_blink method exists
        assert hasattr(container, 'trigger_blink')
        assert callable(container.trigger_blink) 
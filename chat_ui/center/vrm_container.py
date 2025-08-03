from PyQt6.QtWidgets import QWidget, QVBoxLayout
import traceback

# ✅ Import the new WebView-based renderer
from chat_ui.center.vrm_webview import VRMWebView

class VRMContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent; border: 2px solid red;")
        
        # ✅ Use VRMWebView instead of VRMRenderer
        self.vrm_renderer = VRMWebView()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vrm_renderer)

        self.vrm_path = None
    
    def load_vrm(self, vrm_path: str):
        """
        Loads the VRM model into the embedded Three.js viewer.
        """
        print(f"🟢 Loading VRM into WebView: {vrm_path}")
        self.vrm_renderer.load_vrm(vrm_path)
    
    def trigger_blink(self):
        """
        Manually trigger a blink animation on the current VRM model.
        """
        print(f"🟢 Triggering blink on VRM model")
        self.vrm_renderer.trigger_blink()
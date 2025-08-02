from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt
from chat_ui.center.vrm_webview import VRMWebView
from chat_ui.components.VoiceToggleSwitch import VoiceToggleSwitch


class VRMContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")

        # === Main Layout ===
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === VRM WebView Renderer ===
        self.vrm_renderer = VRMWebView()
        layout.addWidget(self.vrm_renderer)

        # === Floating Voice Toggle Overlay ===
        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("background: transparent;")
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        overlay_layout = QHBoxLayout(self.overlay)
        overlay_layout.setContentsMargins(0, 0, 20, 20)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.voice_toggle = VoiceToggleSwitch()
        self.voice_toggle.setStyleSheet("background-color: transparent;")
        overlay_layout.addWidget(self.voice_toggle)

        self.overlay.setLayout(overlay_layout)

    def resizeEvent(self, event):
        """Ensure overlay spans full container for bottom-right positioning."""
        super().resizeEvent(event)
        self.overlay.resize(self.width(), self.height())

    def load_vrm(self, vrm_path: str):
        """
        Loads the VRM model into the embedded Three.js viewer.
        """
        print(f"🟢 Loading VRM into WebView: {vrm_path}")
        self.vrm_renderer.load_vrm(vrm_path)

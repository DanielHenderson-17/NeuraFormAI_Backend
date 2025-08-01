from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

class VRMContainer(QFrame):
    """
    Placeholder VRM container. 
    Future: Render 3D VRM models here using a rendering engine.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )

        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid red;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("No VRM Loaded", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

    def load_vrm(self, vrm_path: str):
        """
        Temporarily just updates label.
        Later: Integrate a 3D viewer for VRM rendering.
        """
        self.label.setText(f"Loaded VRM:\n{vrm_path}")
        print(f"🟢 [VRMContainer] VRM loaded: {vrm_path}")

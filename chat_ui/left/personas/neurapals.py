from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

class NeuraPalsDialog(QDialog):
    def __init__(self, personas, swap_callback, parent=None):
        """
        :param personas: list of persona dicts ({"name": "...", ...})
        :param swap_callback: function to call when persona is selected
        """
        super().__init__(parent)
        self.setWindowTitle("Choose Your NeuraPal")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet("""
            QDialog {
                background-color: #2c2c2c;
                border-radius: 12px;
            }
            QPushButton {
                background-color: #444;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QLabel {
                color: white;
                font-size: 16px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        label = QLabel("Select a Persona:")
        layout.addWidget(label)

        for persona in personas:
            persona_name = persona.get("name", "Unknown")
            btn = QPushButton(persona_name)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, name=persona_name: self._select_persona(name, swap_callback))
            layout.addWidget(btn)

        self.setMinimumWidth(300)

    def _select_persona(self, name, swap_callback):
        """Handle persona selection and close dialog."""
        swap_callback(name)
        self.accept()

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtGui import QPainter, QColor

class UserMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.bg_color = QColor("#3a3a3a")
        self.border_radius = 10            
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        btn_settings = QPushButton("Settings")
        btn_settings.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_settings.setStyleSheet(self._button_style())

        btn_models = QPushButton("Models")
        btn_models.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_models.setStyleSheet(self._button_style())

        btn_logout = QPushButton("Logout")
        btn_logout.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_logout.setStyleSheet(self._button_style())

        layout.addWidget(btn_settings)
        layout.addWidget(btn_models)
        layout.addWidget(btn_logout)

    def _button_style(self):
        return """
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """

    def paintEvent(self, event):
        """Draw rounded rectangle background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.bg_color)
        painter.setPen(QColor("#555555"))  # Subtle border
        painter.drawRoundedRect(self.rect(), self.border_radius, self.border_radius)
        super().paintEvent(event)

# user_menu_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QCursor
from PyQt6.QtCore import Qt
from chat_ui.left.personas.neurapals import NeuraPalsDialog
from chat_ui.services.persona_service import PersonaService



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
        btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        btn_models = QPushButton("NeuraPals")
        btn_models.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_models.setStyleSheet(self._button_style())
        btn_models.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_models.clicked.connect(self.open_neurapals_menu)

        btn_logout = QPushButton("Logout")
        btn_logout.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_logout.setStyleSheet(self._button_style())
        btn_logout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

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

    def open_neurapals_menu(self):
        """Fetch personas dynamically and open selection dialog."""
        personas = PersonaService.list_personas()
        if not personas:
            print("⚠️ [UserMenuWidget] No personas available")
            return

        def swap_persona(name):
            active_persona = PersonaService.select_persona(name)
            if active_persona:
                print(f"✅ [UserMenuWidget] Persona switched → {active_persona.get('name', name)}")
            else:
                print(f"⚠️ [UserMenuWidget] Failed to switch persona to {name}")

        dialog = NeuraPalsDialog(personas, swap_persona, self)
        dialog.exec()

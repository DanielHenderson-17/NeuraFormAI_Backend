# user_menu_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QMessageBox, QDialog, QMainWindow
from PyQt6.QtGui import QPainter, QColor, QCursor
from PyQt6.QtCore import Qt
from chat_ui.left.personas.neurapals import NeuraPalsDialog
from chat_ui.services.persona_service import PersonaService
from chat_ui.services.auth_client import auth_client, BACKEND_BASE_URL



class UserMenuWidget(QWidget):
    # === UserMenuWidget for managing user-related actions in the sidebar ===
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
        btn_logout.clicked.connect(self.confirm_logout)

        layout.addWidget(btn_settings)
        layout.addWidget(btn_models)
        layout.addWidget(btn_logout)

    # === Style for buttons ===
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
    # === Paint event for rounded background ===
    def paintEvent(self, event):
        """Draw rounded rectangle background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.bg_color)
        painter.setPen(QColor("#555555"))  # Subtle border
        painter.drawRoundedRect(self.rect(), self.border_radius, self.border_radius)
        super().paintEvent(event)

    # === Open NeuraPals menu for persona selection ===
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

    def confirm_logout(self):
        m = QMessageBox(self)
        m.setWindowTitle("Sign out")
        m.setText("Do you want to log out?")
        m.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok)
        m.setDefaultButton(QMessageBox.StandardButton.Ok)
        if m.exec() == QMessageBox.StandardButton.Ok:
            # Invalidate backend session and clear local token
            try:
                import requests
                requests.post(
                    f"{BACKEND_BASE_URL}/auth/logout",
                    headers=auth_client.get_headers(),
                    timeout=10,
                )
            except Exception:
                pass
            auth_client.clear_session_token()
            # Hide main window, show login dialog, then re-show main on success
            top = self.window()
            if isinstance(top, QMainWindow):
                top.hide()
            from chat_ui.components.LoginDialog import LoginDialog
            dlg = LoginDialog(None)
            code = dlg.exec()
            if code == QDialog.DialogCode.Accepted:
                if isinstance(top, QMainWindow):
                    top.show()
            else:
                from PyQt6.QtWidgets import QApplication
                QApplication.instance().quit()

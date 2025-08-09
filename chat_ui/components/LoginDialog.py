from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit,
    QFormLayout, QDialogButtonBox, QMessageBox
)

from chat_ui.services.auth_client import auth_client, LoginResult


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sign in")
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        self.status_label = QLabel("Sign in to continue")
        layout.addWidget(self.status_label)

        # Google button
        btn_row = QHBoxLayout()
        self.google_btn = QPushButton("  Continue with Google")
        self.google_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        icon = QIcon(QPixmap("chat_ui/assets/google.svg"))
        self.google_btn.setIcon(icon)
        btn_row.addWidget(self.google_btn)
        layout.addLayout(btn_row)

        # Divider
        layout.addWidget(QLabel("or"), alignment=Qt.AlignmentFlag.AlignHCenter)

        # Email/password (optional now; non-functional placeholder)
        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit(); self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Name", self.name_edit)
        form.addRow("Email", self.email_edit)
        form.addRow("Password", self.password_edit)
        layout.addLayout(form)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.buttons)

        self.google_btn.clicked.connect(self.on_google)
        self.buttons.rejected.connect(self.reject)

        self.session_token: str | None = None

    def on_google(self):
        try:
            self.status_label.setText("Opening Google sign-in…")
            result: LoginResult = auth_client.login_with_google()
        except Exception as e:
            self.status_label.setText("Login failed")
            QMessageBox.critical(self, "Login failed", str(e))
            return

        if result.success and result.session_token:
            self.session_token = result.session_token
            self.accept()
            return

        if result.requires_registration:
            # Minimal registration prompt (birthdate only; other fields from token)
            from PyQt6.QtWidgets import QInputDialog
            bdate, ok = QInputDialog.getText(self, "Complete registration", "Birthdate (YYYY-MM-DD):")
            if not ok or not bdate:
                return
            ok, token, err = auth_client.complete_registration(
                provider_user_id=result.token_sub or "",
                first_name=result.token_first_name or "",
                last_name=result.token_last_name or "",
                email=result.token_email or "",
                birthdate=bdate,
            )
            if not ok:
                self.status_label.setText("Registration failed")
                QMessageBox.critical(self, "Registration failed", err or "unknown error")
                return
            self.status_label.setText("Signed in")
            self.session_token = token
            self.accept()
            return

        QMessageBox.warning(self, "Login failed", result.message or "Unknown error")



from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QApplication, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QCursor
from chat_ui.left.user_menu.user_menu_widget import UserMenuWidget
from chat_ui.services.persona_service import SessionManager


class UserContainer(QFrame):
    # UserContainer for managing user interactions in the left sidebar
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
            }
        """)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)

        # User menu
        self.user_menu = UserMenuWidget(self)
        self.user_menu.setMaximumHeight(0)

        # === Avatar + User ID Container ===
        self.avatar_container = QHBoxLayout()
        self.avatar_container.setContentsMargins(0, 0, 0, 0)
        self.avatar_container.setSpacing(8)

        self.avatar = QLabel("img")
        self.avatar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.avatar.setFixedSize(30, 30)
        self.avatar.setStyleSheet("""
            background-color: blue;
            border-radius: 15px;
            color: white;
        """)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # User ID label
        user_id = SessionManager.get_user_id()
        self.user_id_label = QLabel(user_id[:])  # Show only first 8 chars
        self.user_id_label.setStyleSheet("color: white; font-size: 11px;")
        self.user_id_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Add avatar and ID to container
        self.avatar_container.addWidget(self.avatar)
        self.avatar_container.addWidget(self.user_id_label)

        # === Add to main layout ===
        self.layout.addStretch()
        self.layout.addWidget(self.user_menu)
        self.layout.setSpacing(15)

        # Wrap avatar container in a QWidget to properly add to layout
        avatar_widget = QFrame()
        avatar_widget.setLayout(self.avatar_container)
        self.layout.addWidget(avatar_widget, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        # Menu toggle
        self.menu_visible = False
        self.avatar.mousePressEvent = self.toggle_menu

        QApplication.instance().installEventFilter(self)

    def toggle_menu(self, event):
        current_height = self.user_menu.maximumHeight()
        target_height = self.user_menu.sizeHint().height()
        self.menu_visible = current_height < target_height
        self.animate_menu()

    def animate_menu(self):
        animation = QPropertyAnimation(self.user_menu, b"maximumHeight")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        if self.menu_visible:
            target_height = self.user_menu.sizeHint().height()
            animation.setStartValue(self.user_menu.maximumHeight())
            animation.setEndValue(target_height)
        else:
            animation.setStartValue(self.user_menu.height())
            animation.setEndValue(0)
        animation.start()
        self.animation = animation

    def eventFilter(self, watched, event):
        if self.menu_visible and event.type() == QEvent.Type.MouseButtonPress:
            if not self.user_menu.geometry().contains(
                self.mapFromGlobal(event.globalPosition().toPoint())
            ):
                self.toggle_menu(None)
        return super().eventFilter(watched, event)

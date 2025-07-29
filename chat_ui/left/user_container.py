from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QCursor
from chat_ui.left.user_menu.user_menu_widget import UserMenuWidget

class UserContainer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
            }
        """)
        self.setMinimumWidth(100)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(0)

        self.user_menu = UserMenuWidget(self)
        self.user_menu.setMaximumHeight(0)

        self.avatar = QLabel("img")
        self.avatar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.avatar.setFixedSize(30, 30)
        self.avatar.setStyleSheet("""
            background-color: blue;
            border-radius: 15px;
            color: white;
        """)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()

        # ✅ Add menu and give it bottom margin to push away from avatar
        self.layout.addWidget(self.user_menu)
        self.layout.setSpacing(15)  # increases gap between menu and avatar

        self.layout.addWidget(
            self.avatar,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
        )

        self.menu_visible = False
        self.avatar.mousePressEvent = self.toggle_menu

        QApplication.instance().installEventFilter(self)

    def toggle_menu(self, event):
        current_height = self.user_menu.maximumHeight()
        target_height = self.user_menu.sizeHint().height()

        # ✅ If menu is currently expanded → close it
        if current_height >= target_height:
            self.menu_visible = False
        else:
            self.menu_visible = True

        self.animate_menu()

    def animate_menu(self):
        animation = QPropertyAnimation(self.user_menu, b"maximumHeight")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        if self.menu_visible:
            # ✅ Remove resetting height to 0 before opening
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

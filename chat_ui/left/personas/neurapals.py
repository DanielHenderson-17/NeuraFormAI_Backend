from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QGridLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

class NeuraPalsDialog(QDialog):
    def __init__(self, personas, swap_callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Your NeuraPal")
        self.setModal(False)
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # === Main layout ===
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === Inner frame with rounded background ===
        background_frame = QFrame()
        background_frame.setObjectName("BackgroundFrame")
        bg_layout = QVBoxLayout(background_frame)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.setSpacing(10)

        label = QLabel("Select a NeuraPal:")
        bg_layout.addWidget(label)

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)

        columns = 3
        for idx, persona in enumerate(personas):
            row = idx // columns
            col = idx % columns

            persona_widget = QWidget()
            persona_layout = QVBoxLayout(persona_widget)
            persona_layout.setContentsMargins(0, 0, 0, 0)
            persona_layout.setSpacing(5)

            avatar = QLabel()
            avatar.setObjectName("AvatarBubble")
            avatar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            avatar.mousePressEvent = lambda e, name=persona.get("name", "Unknown"): self._select_persona(name, swap_callback)

            name_label = QLabel(persona.get("name", "Unknown"))
            name_label.setObjectName("NameLabel")

            persona_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
            persona_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)

            grid_layout.addWidget(persona_widget, row, col)

        bg_layout.addWidget(grid_widget)
        main_layout.addWidget(background_frame)

        self.setStyleSheet("""
            QFrame#BackgroundFrame {
                background-color: #333;
                border-radius: 15px;
                border: 1px solid #555;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLabel#AvatarBubble {
                background-color: #444;
                border-radius: 15px;
                min-width: 50px;
                min-height: 50px;
                max-width: 50px;
                max-height: 50px;
                qproperty-alignment: 'AlignCenter';
            }
            QLabel#NameLabel {
                color: white;
                font-size: 12px;
                qproperty-alignment: 'AlignCenter';
            }
        """)

        self.setMinimumWidth(400)

    def _select_persona(self, name, swap_callback):
        swap_callback(name)
        self.accept()

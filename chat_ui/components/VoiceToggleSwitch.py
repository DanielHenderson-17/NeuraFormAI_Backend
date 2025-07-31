from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPainter, QBrush


class VoiceToggleSwitch(QWidget):
    # === VoiceToggleSwitch for enabling/disabling voice features ===
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 24)
        self._enabled = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    # === Check if voice is enabled ===
    def is_enabled(self):
        return self._enabled

    # === Set the enabled state and update appearance ===
    def set_enabled(self, value: bool):
        self._enabled = value
        self.update()

    # === Handle mouse press to toggle state ===
    def mousePressEvent(self, event):
        self._enabled = not self._enabled
        self.update()

    # === Paint the toggle switch appearance ===
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background pill
        bg_color = QColor("#6610f2") if self._enabled else QColor("#444")
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

        # Circle toggle
        knob_radius = 20
        knob_x = self.width() - knob_radius - 2 if self._enabled else 2
        knob_color = QColor("#fff")
        painter.setBrush(QBrush(knob_color))
        painter.drawEllipse(knob_x, 2, knob_radius, knob_radius)


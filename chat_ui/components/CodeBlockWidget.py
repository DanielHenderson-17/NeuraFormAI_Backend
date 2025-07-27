from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QApplication
)
from PyQt6.QtGui import QFont, QIcon, QClipboard
from PyQt6.QtCore import Qt, QSize
import os


class CodeBlockWidget(QWidget):
    def __init__(self, code: str, language: str = "code"):
        super().__init__()

        self.language = language.strip() if language else "code"

        self.setStyleSheet("""
            QWidget#CodeBlockContainer {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 8px;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setObjectName("CodeBlockContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(6)

        # === Header ===
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        lang_label = QLabel(self.language)
        lang_label.setStyleSheet("color: #bbb; font-size: 12px;")
        header_layout.addWidget(lang_label)
        header_layout.addStretch()

        self.copy_btn = QPushButton("Copy")
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'copy.svg')
        self.copy_btn.setIcon(QIcon(os.path.abspath(icon_path)))
        self.copy_btn.setIconSize(QSize(10, 10))
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                font-size: 12px;
                border: none;
                padding: 0px 4px;
            }
            QPushButton:hover {
                background-color: #333;
                border-radius: 4px;
            }
        """)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        header_layout.addWidget(self.copy_btn)

        self.text_edit = QTextEdit()
        self.text_edit.setText(code.strip())
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier", 10))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: #dcdcdc;
                border: none;
            }
        """)
        self.text_edit.setFixedHeight(self.calculate_text_height())

        container_layout.addWidget(header)
        container_layout.addWidget(self.text_edit)
        self.container.setLayout(container_layout)
        outer_layout.addWidget(self.container)

    def calculate_text_height(self):
        line_count = self.text_edit.toPlainText().count('\n') + 1
        font_metrics = self.text_edit.fontMetrics()
        return line_count * font_metrics.lineSpacing() + 16

    def copy_to_clipboard(self):
        clipboard: QClipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())

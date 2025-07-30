import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from chat_ui.center.center_column_container import CenterColumnContainer
from chat_ui.left.left_column_container import LeftColumnContainer
from chat_ui.right.right_column_container import RightColumnContainer

sys.path.append(str(Path(__file__).resolve().parent.parent))

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("chat_ui/assets/neuraform_icon.png"))

    window = QMainWindow()
    window.setWindowTitle("NeuraPals - AI Chat")
    window.resize(1400, 700)

    main_widget = QWidget()
    layout = QGridLayout(main_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # === Left column
    left_column = LeftColumnContainer()
    layout.addWidget(left_column, 0, 0, 2, 1)

    # === Center column (now includes chat_input internally)
    center_column = CenterColumnContainer()
    layout.addWidget(center_column, 0, 1, 2, 1)  # spans both rows

    # === Right column
    right_column = RightColumnContainer()
    layout.addWidget(right_column, 0, 2, 2, 1)

    # Wire up
    center_column.chat_input.chat_window = right_column.chat_window
    right_column.chat_window.input_box = center_column.chat_input

    # ✅ Column proportions
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 2)
    layout.setColumnStretch(2, 1)

    window.setCentralWidget(main_widget)
    window.move(app.primaryScreen().availableGeometry().center() - window.rect().center())
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

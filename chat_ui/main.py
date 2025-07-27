import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon  # ← Make sure this is imported
from chat_ui.chat_window import ChatWindow

# Add parent path for module resolution
sys.path.append(str(Path(__file__).resolve().parent.parent))

def main():
    app = QApplication(sys.argv)

    # ✅ THIS is the only new line you need
    app.setWindowIcon(QIcon("chat_ui/assets/neuraform_icon.png"))

    window = QMainWindow()
    chat = ChatWindow()
    window.setCentralWidget(chat)
    window.setWindowTitle("NeuraForm - AI Chat")
    window.resize(900, 700)
    window.move(
        app.primaryScreen().availableGeometry().center() - window.rect().center()
    )
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

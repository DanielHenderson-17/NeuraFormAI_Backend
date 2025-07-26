import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PyQt6.QtWidgets import QApplication, QMainWindow
from chat_ui.chat_window import ChatWindow

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    chat = ChatWindow()
    window.setCentralWidget(chat)
    window.setWindowTitle("NeuraForm - AI Chat")
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

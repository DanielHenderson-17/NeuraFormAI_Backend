import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap

from chat_ui.center.center_column_container import CenterColumnContainer
from chat_ui.left.left_column_container import LeftColumnContainer
from chat_ui.right.right_column_container import RightColumnContainer
from chat_ui.services.persona_service import PersonaService

# === Ensure the chat_ui directory is in the Python path for imports ===
sys.path.append(str(Path(__file__).resolve().parent.parent))

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("chat_ui/assets/neuraform_icon.png"))

    # === 1️⃣ Show splash screen
    splash_pix = QPixmap("chat_ui/assets/neurapal_ai_splash.png")
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # === 2️⃣ Setup main window
    window = QMainWindow()
    window.setWindowTitle("NeuraPal - AI Chat")
    window.resize(1400, 700)

    main_widget = QWidget()
    layout = QGridLayout(main_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # === Left column
    left_column = LeftColumnContainer()
    layout.addWidget(left_column, 0, 0, 2, 1)

    # === Center column (includes chat_input internally)
    center_column = CenterColumnContainer()
    layout.addWidget(center_column, 0, 1, 2, 1)

    # === Right column
    right_column = RightColumnContainer()
    layout.addWidget(right_column, 0, 2, 2, 1)

    # ✅ Wire up chat input and window
    center_column.chat_input.chat_window = right_column.chat_window
    right_column.chat_window.input_box = center_column.chat_input

    # ✅ Register components with PersonaService
    PersonaService.register_chat_window(right_column.chat_window)
    PersonaService.register_vrm_container(center_column.vrm_container)

    # ✅ Auto-load active persona VRM on startup
    active_persona = PersonaService.get_active_persona()
    if active_persona:
        vrm_model = active_persona.get("vrm_model", "")
        locked = active_persona.get("locked", False)

        if not locked and vrm_model:
            vrm_path = os.path.join(PersonaService.VRM_DIR, vrm_model)
            if os.path.exists(vrm_path):
                center_column.vrm_container.load_vrm(vrm_path)
                print(f"✅ Auto-loaded active persona VRM: {vrm_model}")
            else:
                print(f"⚠️ VRM file missing on startup: {vrm_path}")
        else:
            print("🔒 Active persona is locked or has no VRM.")

    # ✅ Column proportions
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 2)
    layout.setColumnStretch(2, 1)

    # === Final setup
    window.setCentralWidget(main_widget)
    window.move(app.primaryScreen().availableGeometry().center() - window.rect().center())

    # === 3️⃣ Hide splash and show main window
    QTimer.singleShot(1500, splash.close)  # Keeps splash for 1.5s
    QTimer.singleShot(1500, window.show)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

import os
import sys
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# ✅ Set Chromium flags BEFORE PyQt loads
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-features=JavascriptModules"

# === Ensure the chat_ui directory is in the Python path for imports ===
sys.path.append(str(Path(__file__).resolve().parent.parent))

# ✅ Enable OpenGL context sharing for QtWebEngine
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

def main():
    app = QApplication(sys.argv)

    from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QSplashScreen
    from PyQt6.QtCore import QTimer
    from PyQt6.QtGui import QIcon, QPixmap
    from PyQt6.QtWebEngineCore import QWebEngineProfile

    from chat_ui.center.center_column_container import CenterColumnContainer
    from chat_ui.left.left_column_container import LeftColumnContainer
    from chat_ui.right.right_column_container import RightColumnContainer
    from chat_ui.services.persona_service import PersonaService

    # ✅ Enable ES module support in Chromium
    QWebEngineProfile.defaultProfile().setHttpAcceptLanguage("en-US,en")

    app.setWindowIcon(QIcon("chat_ui/assets/neuraform_icon.png"))

    # === Splash screen
    splash_pix = QPixmap("chat_ui/assets/neurapal_ai_splash.png")
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # === Main window
    window = QMainWindow()
    window.setWindowTitle("NeuraPal - AI Chat")
    window.resize(1400, 700)

    main_widget = QWidget()
    layout = QGridLayout(main_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    left_column = LeftColumnContainer()
    layout.addWidget(left_column, 0, 0, 2, 1)

    center_column = CenterColumnContainer()
    layout.addWidget(center_column, 0, 1, 2, 1)

    right_column = RightColumnContainer()
    layout.addWidget(right_column, 0, 2, 2, 1)

    center_column.chat_input.chat_window = right_column.chat_window
    right_column.chat_window.input_box = center_column.chat_input

    PersonaService.register_chat_window(right_column.chat_window)
    PersonaService.register_vrm_container(center_column.vrm_container)

    # 🎭 Connect VRM viewer to expression manager
    from chat_ui.right.chat_window import vrm_expression_manager
    vrm_expression_manager.set_vrm_viewer(center_column.vrm_container.vrm_renderer)
    print("🎭 VRM Expression System connected!")

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

    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 2)
    layout.setColumnStretch(2, 1)

    window.setCentralWidget(main_widget)
    window.move(app.primaryScreen().availableGeometry().center() - window.rect().center())

    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, window.show)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

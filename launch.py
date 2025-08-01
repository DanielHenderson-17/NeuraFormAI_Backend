import os
import sys
import subprocess
import importlib.util

# ✅ Set Chromium flags BEFORE PyQt loads
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-features=JavascriptModules"

print("🚀 Launching NeuraForm UI with ES module support...")

# === 🔍 Detect early WebEngine imports ===
def check_webengine_imports():
    risky_modules = [
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineQuick",
        "PyQt6.QtWebEngine"
    ]
    found = []
    
    for mod in risky_modules:
        if importlib.util.find_spec(mod) is not None and mod in sys.modules:
            found.append(mod)

    if found:
        print("⚠️ WARNING: WebEngine modules imported too early:", found)
        print("⚠️ This can break Chromium initialization (QApplication must be created first).")

check_webengine_imports()

# ✅ Run main.py with flags applied
try:
    exit_code = subprocess.call([sys.executable, "-m", "chat_ui.main"])
    sys.exit(exit_code)
except KeyboardInterrupt:
    print("\n🛑 Launch interrupted by user.")
    sys.exit(1)

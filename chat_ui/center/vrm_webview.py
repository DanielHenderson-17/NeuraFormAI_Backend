import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QTimer, QUrl, QObject, pyqtSlot, QSize
from PyQt6.QtGui import QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
# Re-import QWebEngineSettings as it's needed for setAttribute
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings 

class JSConsoleHandler(QWebEnginePage):
    """
    Custom QWebEnginePage to override the JavaScript console message handler.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set the QWebEnginePage's background color to transparent
        self.setBackgroundColor(QColor(0, 0, 0, 0))

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        # A compatible way to map console message levels,
        # since ConsoleMessageLevel might not be available in older versions.
        level_map = {
            0: "DEBUG",
            1: "INFO",
            2: "WARN",
            3: "ERROR",
        }
        level_str = level_map.get(level, "UNKNOWN")
        
        # Don't print empty messages
        if message.strip():
            print(f"🔴 [JS Console][{level_str}] {message} (at {sourceId}:{lineNumber})")
        # Call the default handler to ensure messages are still logged if needed
        super().javaScriptConsoleMessage(level, message, lineNumber, sourceId)

class JSLogger(QObject):
    """
    Exposes a Python object to the JavaScript environment to handle console logs.
    """
    @pyqtSlot(str)
    def logMessage(self, message):
        print(f"🟢 [JS Log] {message}")


class VRMWebView(QWidget):
    """
    A QWidget containing a QWebEngineView to render the VRM viewer HTML.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # We can also set the parent widget's background to transparent for good measure
        self.setStyleSheet("background: transparent;")
        
        # Create a QWebEngineView and set our custom page for it
        self.webview = QWebEngineView(self)
        custom_page = JSConsoleHandler(self.webview)
        self.webview.setPage(custom_page)
        
        # Enable JavaScript and local file access 
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # Set up a channel to allow Python and JavaScript to communicate
        self.channel = QWebChannel()
        self.logger = JSLogger()
        self.channel.registerObject("pyLogger", self.logger)
        self.webview.page().setWebChannel(self.channel)
        
        self.layout.addWidget(self.webview)

        # Build the absolute path to the HTML file relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.normpath(os.path.join(script_dir, "../assets/vrm_viewer/index.html"))
        
        # Verify the HTML file exists
        if not os.path.exists(html_path):
            print(f"❌ Error: HTML file not found at {html_path}")
            self.webview.setHtml(f"<h1>Error: index.html not found!</h1><p>Expected at: {html_path}</p>")
        else:
            print(f"Loading HTML from: {html_path}")
            self.webview.load(QUrl.fromLocalFile(html_path))

        self._pending_vrm = None
        self._check_timer = QTimer(self)
        self._check_timer.setInterval(300)
        self._check_timer.timeout.connect(self._check_ready)

    def load_vrm(self, vrm_path: str):
        print(f"🟢 [Python] Received VRM path: {vrm_path}")
        
        vrm_abs_path = os.path.abspath(vrm_path)
        vrm_url = QUrl.fromLocalFile(vrm_abs_path).toString()
        
        print(f"🟢 [Python] Converted to URL: {vrm_url}")
        
        self._pending_vrm = vrm_url
        self._check_timer.start()

    def _check_ready(self):
        js_check = "window.vrmViewerReady === true;"
        self.webview.page().runJavaScript(js_check, self._on_ready_check)

    def _on_ready_check(self, ready):
        if ready:
            self._check_timer.stop()
            print("🟢 [Python] VRM Viewer is ready, loading model...")
            js_load = f'window.loadVRM("{self._pending_vrm}");'
            self.webview.page().runJavaScript(js_load)
        else:
            print("🟡 [Python] VRM Viewer not ready, retrying...")
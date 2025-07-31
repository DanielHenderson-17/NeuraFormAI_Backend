import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from chat_ui.components.CodeBlockWidget import CodeBlockWidget

# === Fixture for CodeBlockWidget ===
@pytest.fixture
def widget(qtbot):
    code = "print('Hello')\nprint('World')"
    w = CodeBlockWidget(code=code, language="python")
    qtbot.addWidget(w)
    return w

# === Test: Initial state of CodeBlockWidget ===
def test_initial_state(widget):
    """Ensure widget initializes with correct text and language."""
    assert widget.text_edit.toPlainText() == "print('Hello')\nprint('World')"
    assert widget.language == "python"
    # Validate calculated height is greater than 0
    assert widget.text_edit.height() > 0

# === Test: Copy button functionality ===
def test_calculate_text_height(widget):
    """Verify calculated height matches expected line count."""
    lines = widget.text_edit.toPlainText().count("\n") + 1
    expected_height = lines * widget.text_edit.fontMetrics().lineSpacing() + 16
    assert widget.calculate_text_height() == expected_height

# === Test: Copy to clipboard functionality ===
def test_copy_to_clipboard(widget, qtbot):
    """Ensure copy button places text into the clipboard."""
    clipboard = QApplication.clipboard()
    clipboard.clear()
    
    qtbot.mouseClick(widget.copy_btn, Qt.MouseButton.LeftButton)
    
    assert clipboard.text() == "print('Hello')\nprint('World')"

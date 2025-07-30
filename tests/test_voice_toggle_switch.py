import pytest
from PyQt6.QtCore import Qt
from chat_ui.components.VoiceToggleSwitch import VoiceToggleSwitch


@pytest.fixture
def widget(qtbot):
    w = VoiceToggleSwitch()
    qtbot.addWidget(w)
    return w


def test_initial_state(widget):
    """Ensure the toggle starts disabled."""
    assert widget.is_enabled() is False


def test_set_enabled_changes_state(widget):
    """Directly setting enabled updates the state."""
    widget.set_enabled(True)
    assert widget.is_enabled() is True
    widget.set_enabled(False)
    assert widget.is_enabled() is False


def test_click_toggles_state(widget, qtbot):
    """Clicking the widget toggles its state."""
    qtbot.mouseClick(widget, Qt.MouseButton.LeftButton)
    assert widget.is_enabled() is True
    qtbot.mouseClick(widget, Qt.MouseButton.LeftButton)
    assert widget.is_enabled() is False


def test_paint_event_runs(widget, qtbot):
    """Ensure paintEvent runs without errors (manual rendering check)."""
    widget.set_enabled(True)
    widget.repaint()  # triggers paintEvent
    assert widget.is_enabled() is True

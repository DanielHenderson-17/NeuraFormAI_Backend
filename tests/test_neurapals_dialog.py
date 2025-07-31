import pytest
from PyQt6.QtCore import Qt
from chat_ui.left.personas.neurapals import NeuraPalsDialog

# === Fixture for NeuraPalsDialog ===
@pytest.fixture
def personas():
    return [
        {"name": "Fuka"},
        {"name": "Nika"},
        {"name": "Kenji"}
    ]

# === Fixture for NeuraPalsDialog with callback ===
@pytest.fixture
def dialog(qtbot, personas):
    callback_called = {"name": None}

    def mock_callback(name):
        callback_called["name"] = name

    dlg = NeuraPalsDialog(personas, swap_callback=mock_callback)
    qtbot.addWidget(dlg)
    return dlg, callback_called


# === Test: Dialog creates correct number of persona buttons ===
def test_buttons_render(dialog):
    dlg, _ = dialog
    buttons = dlg.findChildren(type(dlg.findChild(type(dlg.layout().itemAt(1).widget()))))
    assert len(buttons) == 3  # matches number of personas


# === Test: Clicking a button triggers swap callback and closes dialog ===
def test_persona_selection_triggers_callback(qtbot, dialog):
    dlg, callback_called = dialog

    buttons = dlg.findChildren(type(dlg.findChild(type(dlg.layout().itemAt(1).widget()))))
    target_button = buttons[1]  # select Nika
    qtbot.mouseClick(target_button, Qt.MouseButton.LeftButton)

    assert callback_called["name"] == "Nika"
    assert dlg.result() == dlg.DialogCode.Accepted

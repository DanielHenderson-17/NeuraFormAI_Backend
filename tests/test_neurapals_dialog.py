import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
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
    
    # Get the background frame which contains the grid
    main_layout = dlg.layout()
    background_frame = main_layout.itemAt(0).widget()
    bg_layout = background_frame.layout()
    
    # The grid widget is at index 1 (after the label)
    grid_widget = bg_layout.itemAt(1).widget()
    assert grid_widget is not None
    
    # Find all avatar labels (QLabel with AvatarBubble object name)
    from PyQt6.QtWidgets import QLabel
    avatar_labels = grid_widget.findChildren(QLabel)
    avatar_labels = [label for label in avatar_labels if label.objectName() == "AvatarBubble"]
    assert len(avatar_labels) == 3  # matches number of personas


# === Test: Clicking a button triggers swap callback and closes dialog ===
def test_persona_selection_triggers_callback(qtbot, dialog):
    dlg, callback_called = dialog

    # Get the background frame which contains the grid
    main_layout = dlg.layout()
    background_frame = main_layout.itemAt(0).widget()
    bg_layout = background_frame.layout()
    
    # The grid widget is at index 1 (after the label)
    grid_widget = bg_layout.itemAt(1).widget()
    
    # Find all avatar labels (QLabel with AvatarBubble object name)
    from PyQt6.QtWidgets import QLabel
    avatar_labels = grid_widget.findChildren(QLabel)
    avatar_labels = [label for label in avatar_labels if label.objectName() == "AvatarBubble"]
    
    # Click on the second avatar label (Nika)
    target_avatar = avatar_labels[1]
    qtbot.mouseClick(target_avatar, Qt.MouseButton.LeftButton)

    assert callback_called["name"] == "Nika"
    assert dlg.result() == dlg.DialogCode.Accepted

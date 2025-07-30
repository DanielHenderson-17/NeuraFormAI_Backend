import pytest
from unittest.mock import MagicMock
from chat_ui.left.user_menu.user_menu_widget import UserMenuWidget


@pytest.fixture
def widget(qtbot, monkeypatch):
    """Fixture to create UserMenuWidget with mocked PersonaService and Dialog."""
    # Mock PersonaService
    monkeypatch.setattr("chat_ui.left.user_menu.user_menu_widget.PersonaService.list_personas", lambda: [{"name": "Fuka"}])
    mock_select = MagicMock(return_value={"name": "Fuka"})
    monkeypatch.setattr("chat_ui.left.user_menu.user_menu_widget.PersonaService.select_persona", mock_select)

    # Mock NeuraPalsDialog
    mock_dialog = MagicMock()
    monkeypatch.setattr("chat_ui.left.user_menu.user_menu_widget.NeuraPalsDialog", lambda personas, cb, parent=None: mock_dialog)

    # Create widget
    w = UserMenuWidget()
    qtbot.addWidget(w)
    return w, mock_dialog, mock_select


def test_buttons_exist(widget):
    w, _, _ = widget
    buttons = w.findChildren(type(w.findChild(type(w.layout().itemAt(0).widget()))))
    assert len(buttons) == 3  # Settings, NeuraPals, Logout


def test_open_neurapals_menu_triggers_dialog(widget):
    w, mock_dialog, mock_select = widget

    # Find the "NeuraPals" button (2nd button)
    btn_models = w.layout().itemAt(1).widget()
    btn_models.click()

    # Verify dialog was created and exec called
    assert mock_dialog.exec.called
    # Simulate selecting persona
    callback = mock_dialog.call_args[0][1]
    callback("Fuka")
    mock_select.assert_called_once_with("Fuka")


def test_open_neurapals_menu_no_personas(qtbot, monkeypatch):
    """Test when no personas are available, dialog does not open."""
    monkeypatch.setattr("chat_ui.left.user_menu.user_menu_widget.PersonaService.list_personas", lambda: [])

    w = UserMenuWidget()
    qtbot.addWidget(w)

    btn_models = w.layout().itemAt(1).widget()
    btn_models.click()  # Should just print warning, no crash

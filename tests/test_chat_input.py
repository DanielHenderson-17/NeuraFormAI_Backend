import pytest
from unittest.mock import MagicMock, patch
from chat_ui.right.chat_window import ChatWindow
import chat_ui.center.chat_input as chat_input_module
from chat_ui.center.chat_input import ChatInput

# === Fixture for VoiceRecorder ===
@pytest.fixture(autouse=True)
def mock_voice_recorder(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(chat_input_module, "VoiceRecorder", lambda: mock)
    yield

# === Fixture for ChatInput ===
@pytest.fixture
def chat_input(qtbot):
    window = ChatWindow()
    input_widget = ChatInput(chat_window=window)
    qtbot.addWidget(input_widget)
    return input_widget

# === Test of the ChatInput functionality ===
def test_initial_state(chat_input):
    assert chat_input.voice_mode is False
    assert chat_input.entry.placeholderText() == "Start typing..."
    assert chat_input.send_button.isEnabled()

# === Test input mode switching ===
def test_switch_to_mic_mode(chat_input):
    chat_input.set_input_mode("mic")
    assert chat_input.voice_mode is True
    assert chat_input.entry.placeholderText() in ("Listening...", "Listening…")
    assert not chat_input.send_button.isEnabled()
    assert chat_input.mic_button.isChecked()

# === Test input mode switching back to keyboard ===
def test_switch_back_to_keyboard(chat_input):
    chat_input.set_input_mode("mic")
    chat_input.set_input_mode("keyboard")
    assert chat_input.voice_mode is False
    assert chat_input.entry.placeholderText() == "Start typing..."
    assert chat_input.send_button.isEnabled()
    assert not chat_input.mic_button.isChecked()

# === Test send message functionality ===
def test_send_message_posts_event(chat_input):
    chat_input.entry.setText("Hello world")
    chat_input.send_message()
    assert chat_input.entry.toPlainText() == ""

# === Test toggle chat window visibility ===
def test_toggle_chat_window(chat_input, qtbot):
    chat_input.chat_window.show()
    assert chat_input.chat_window.isVisible() is True

    chat_input.toggle_chat_window()
    assert chat_input.chat_window.isVisible() is False

    chat_input.toggle_chat_window()
    assert chat_input.chat_window.isVisible() is True

# === Test toggle mic functionality ===
def test_toggle_mic(chat_input):
    assert chat_input.voice_mode is False
    chat_input.toggle_mic()
    assert chat_input.voice_mode is True
    chat_input.toggle_mic()
    assert chat_input.voice_mode is False

# === Test is_voice_enabled method ===
def test_is_voice_enabled(chat_input):
    chat_input.voice_toggle.is_enabled = MagicMock(return_value=True)
    assert chat_input.is_voice_enabled() is True

    chat_input.voice_toggle.is_enabled.return_value = False
    assert chat_input.is_voice_enabled() is False


# === Test persona switching via typed command ===
@patch("chat_ui.center.chat_input.PersonaService.select_persona")
def test_typed_command_switches_persona(mock_select, chat_input):
    chat_input.entry.setText("switch to fuka")
    chat_input.send_message()
    mock_select.assert_called_once_with("fuka")


# === Test update_status behavior ===
def test_update_status_changes_placeholder(chat_input):
    chat_input.update_status("Stopped")
    assert chat_input.voice_mode is False

    chat_input.update_status("Listening")
    assert "Listening" in chat_input.entry.placeholderText()

    chat_input.update_status("Processing...")
    assert chat_input.entry.placeholderText() == "Processing..."

import pytest
from unittest.mock import MagicMock
from chat_ui.right.chat_window import ChatWindow
import chat_ui.center.chat_input as chat_input_module
from chat_ui.center.chat_input import ChatInput


# 🔇 Mock VoiceRecorder globally
@pytest.fixture(autouse=True)
def mock_voice_recorder(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(chat_input_module, "VoiceRecorder", lambda: mock)
    yield


@pytest.fixture
def chat_input(qtbot):
    window = ChatWindow()
    input_widget = ChatInput(chat_window=window)
    qtbot.addWidget(input_widget)
    return input_widget


def test_initial_state(chat_input):
    assert chat_input.voice_mode is False
    assert chat_input.entry.placeholderText() == "Start typing..."
    assert chat_input.send_button.isEnabled()


def test_switch_to_mic_mode(chat_input):
    chat_input.set_input_mode("mic")
    assert chat_input.voice_mode is True
    assert chat_input.entry.placeholderText() in ("Listening...", "Listening…")
    assert not chat_input.send_button.isEnabled()
    assert chat_input.mic_button.isChecked()


def test_switch_back_to_keyboard(chat_input):
    chat_input.set_input_mode("mic")
    chat_input.set_input_mode("keyboard")
    assert chat_input.voice_mode is False
    assert chat_input.entry.placeholderText() == "Start typing..."
    assert chat_input.send_button.isEnabled()
    assert not chat_input.mic_button.isChecked()


def test_send_message_posts_event(chat_input):
    chat_input.entry.setText("Hello world")
    chat_input.send_message()
    assert chat_input.entry.toPlainText() == ""


def test_toggle_chat_window(chat_input, qtbot):
    chat_input.chat_window.show()
    assert chat_input.chat_window.isVisible() is True

    chat_input.toggle_chat_window()
    assert chat_input.chat_window.isVisible() is False

    chat_input.toggle_chat_window()
    assert chat_input.chat_window.isVisible() is True


# 🎙️ Test: toggle_mic switches correctly
def test_toggle_mic(chat_input):
    assert chat_input.voice_mode is False
    chat_input.toggle_mic()
    assert chat_input.voice_mode is True
    chat_input.toggle_mic()
    assert chat_input.voice_mode is False


# ✅ Test: is_voice_enabled reflects toggle state
def test_is_voice_enabled(chat_input):
    # Mock VoiceToggleSwitch to control return value
    chat_input.voice_toggle.is_enabled = MagicMock(return_value=True)
    assert chat_input.is_voice_enabled() is True

    chat_input.voice_toggle.is_enabled.return_value = False
    assert chat_input.is_voice_enabled() is False

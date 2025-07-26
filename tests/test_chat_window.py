import pytest
from PyQt6.QtWidgets import QApplication
from chat_ui.chat_window import ChatWindow


# 🧪 chat_window Fixture
# Creates a fresh instance of ChatWindow and registers it with the Qt test bot.
@pytest.fixture
def chat_window(qtbot):
    window = ChatWindow()
    qtbot.addWidget(window)
    return window


# ✅ Test: Initial state of the ChatWindow
# Ensures correct placeholders and button states on startup.
def test_initial_state(chat_window):
    assert chat_window.entry.placeholderText() == "Start typing..."
    assert chat_window.send_button.isEnabled()
    assert not chat_window.voice_mode


# ✅ Test: Sending a message should create a new chat bubble
def test_send_message_adds_bubble(chat_window, qtbot):
    chat_window.entry.setText("Hello test")
    chat_window.send_message()

    # Check if a bubble was added to the scroll layout
    assert chat_window.scroll_layout.count() > 0
    bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
    assert "Hello test" in bubble.message


# 🎙️ Test: Switching to microphone mode updates UI state
def test_set_input_mode_mic(chat_window):
    chat_window.set_input_mode("mic")
    assert chat_window.entry.placeholderText() == "Listening..."
    assert not chat_window.send_button.isEnabled()
    assert chat_window.voice_mode is True


# ⌨️ Test: Switching back to keyboard mode resets UI properly
def test_set_input_mode_keyboard(chat_window):
    chat_window.set_input_mode("keyboard")
    assert chat_window.entry.placeholderText() == "Start typing..."
    assert chat_window.send_button.isEnabled()
    assert chat_window.voice_mode is False

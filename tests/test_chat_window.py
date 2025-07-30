import pytest
from PyQt6.QtCore import QEvent
from chat_ui.right.chat_window import ChatWindow, TypingEvent, ReplyEvent


@pytest.fixture
def chat_window(qtbot):
    """Creates a fresh instance of ChatWindow for each test."""
    window = ChatWindow()
    qtbot.addWidget(window)
    return window


# ✅ Test: Adding a user message bubble
def test_add_user_bubble(chat_window):
    chat_window.add_bubble("Hello user", sender="user")

    assert chat_window.scroll_layout.count() > 0
    bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
    assert "Hello user" in bubble.message
    assert bubble.align_right is True  # User messages are right-aligned


# ✅ Test: Adding an AI message bubble
def test_add_ai_bubble(chat_window):
    chat_window.add_bubble("Hello AI", sender="ai")

    bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
    assert "Hello AI" in bubble.message
    assert bubble.align_right is False  # AI messages are left-aligned


# 💬 Test: Typing bubble insertion
def test_insert_typing_bubble(chat_window):
    chat_window.insert_typing_bubble()

    assert chat_window.typing_label is not None
    assert chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget() == chat_window.typing_label


# 🧹 Test: Removing typing bubble
def test_remove_typing_bubble(chat_window):
    chat_window.insert_typing_bubble()
    chat_window.remove_typing_bubble()

    assert chat_window.typing_label is None
    assert chat_window.typing_timer is None


# 🔄 Test: Handling ReplyEvent adds an AI bubble
def test_reply_event_adds_bubble(chat_window):
    event = ReplyEvent("AI says hi")
    chat_window.event(event)

    bubble = chat_window.scroll_layout.itemAt(chat_window.scroll_layout.count() - 1).widget()
    assert "AI says hi" in bubble.message
    assert bubble.align_right is False

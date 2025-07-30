import pytest
from PyQt6.QtWidgets import QApplication
from chat_ui.right.chat_bubble import ChatBubble


# 🧪 Pytest fixture to initialize QApplication (required for Qt widgets)
@pytest.fixture
def app(qtbot):
    return QApplication([])


# 💬 Test left-aligned chat bubble (e.g., from bot or assistant)
def test_chat_bubble_left(qtbot):
    bubble = ChatBubble("Hello world", "Bot", align_right=False)
    qtbot.addWidget(bubble)

    assert bubble.sender_name == "Bot"                   # ✅ Correct sender
    assert "Hello world" in bubble.message               # ✅ Message content matches
    assert bubble.align_right is False                   # ✅ Left alignment


# 💬 Test right-aligned chat bubble (e.g., from user)
def test_chat_bubble_right(qtbot):
    bubble = ChatBubble("Hi there", "User", align_right=True)
    qtbot.addWidget(bubble)

    assert bubble.sender_name == "User"                  # ✅ Sender name is "User"
    assert bubble.align_right is True                    # ✅ Right alignment enabled

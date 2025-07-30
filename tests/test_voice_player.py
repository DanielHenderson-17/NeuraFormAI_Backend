import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from chat_ui.components.VoicePlayer import VoicePlayer


@pytest.fixture
def player():
    return VoicePlayer()


def test_voice_disabled_skips_playback(player, capsys):
    player.play_reply_from_backend("Hello", voice_enabled=False)
    captured = capsys.readouterr()
    assert "Voice disabled" in captured.out


class FakeAudio:
    def __init__(self):
        self.channels = 1
        self.frame_rate = 44100
        self.array_type = 'h'

    def get_array_of_samples(self):
        return np.array([0, 1, -1, 0], dtype=np.int16)

    def __sub__(self, other):
        return self

    def __len__(self):
        # Simulate audio duration in ms
        return 1000


@patch("chat_ui.components.VoicePlayer.requests.post")
@patch("chat_ui.components.VoicePlayer.sd")
def test_successful_playback(mock_sd, mock_post, player, monkeypatch):
    monkeypatch.setattr("chat_ui.components.VoicePlayer.AudioSegment.converter", "fake_ffmpeg")

    with patch("chat_ui.components.VoicePlayer.AudioSegment.from_file", return_value=FakeAudio()) as mock_from_file:
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b"fake-mp3-data"]
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_post.return_value = mock_response

        called = {"on_start": False}
        def cb():
            called["on_start"] = True

        player.play_reply_from_backend("Test message", voice_enabled=True, on_start=cb)

        mock_from_file.assert_called_once()
        mock_sd.play.assert_called_once()
        mock_sd.wait.assert_called_once()
        assert called["on_start"] is True

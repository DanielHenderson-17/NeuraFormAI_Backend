import pytest
from unittest.mock import MagicMock, patch
from chat_ui.voice_recorder import VoiceRecorder
import numpy as np
import itertools


# 🧪 Fixture: Create a VoiceRecorder instance with the "tiny" model
@pytest.fixture
def recorder():
    return VoiceRecorder(model_name="tiny")


# ✅ Test: Initialization defaults are set correctly
def test_init_defaults(recorder):
    assert recorder.sample_rate == 16000
    assert recorder.block_size == 480
    assert recorder.continuous_mode is True
    assert recorder.max_empty_loops == 3


# 🎙️ Test: Recording stops after silence is detected
# Mocks the VAD to always return "not speech", and fakes time to simulate silence timeout
@patch("chat_ui.voice_recorder.sd.InputStream")
@patch.object(VoiceRecorder, "_is_speech", return_value=False)
def test_record_until_silence(mock_is_speech, mock_stream, recorder):
    recorder.recording = True
    recorder.audio_queue.put(np.zeros(recorder.block_size, dtype=np.float32))
    recorder.audio_queue.put(np.zeros(recorder.block_size, dtype=np.float32))
    recorder.audio_queue.put(np.zeros(recorder.block_size, dtype=np.float32))

    # Fake advancing time to trigger silence duration cutoff
    fake_time = itertools.count(start=0, step=2)  # 0, 2, 4, 6, 8...
    with patch("time.time", side_effect=lambda: next(fake_time)):
        audio = recorder._record_until_silence()

    assert isinstance(audio, np.ndarray)
    assert audio.size > 0


# 🧠 Test: Mocked transcription returns concatenated text
# Bypasses the WhisperModel by injecting a MagicMock with fake segments
def test_transcribe_mocked(recorder):
    dummy_audio = np.zeros(16000, dtype=np.float32)
    recorder.model = MagicMock()
    recorder.model.transcribe.return_value = (
        [MagicMock(text="hello"), MagicMock(text="world")],
        None
    )
    result = recorder._transcribe(dummy_audio)
    assert result == "hello world"

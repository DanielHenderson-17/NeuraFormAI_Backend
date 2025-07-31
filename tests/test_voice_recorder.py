import pytest
from unittest.mock import MagicMock, patch
from chat_ui.voice_recorder import VoiceRecorder
import numpy as np
import itertools
import threading
import time


@pytest.fixture
def recorder():
    """Fixture: Create a VoiceRecorder instance with a small model to speed tests."""
    return VoiceRecorder(model_name="tiny")


# ✅ Test: Initialization defaults are set correctly
def test_init_defaults(recorder):
    assert recorder.sample_rate == 16000
    assert recorder.block_size == 480
    assert recorder.continuous_mode is True
    assert recorder.max_empty_loops == 3
    assert callable(recorder._is_speech)


# 🎙️ Test: Audio callback adds data to queue
def test_callback_adds_to_queue(recorder):
    dummy_data = np.ones((10, 1), dtype=np.float32)
    recorder._callback(dummy_data, frames=10, time_info=None, status=None)
    assert not recorder.audio_queue.empty()


# 🎙️ Test: _is_speech returns True/False via vad
def test_is_speech_detection(recorder):
    pcm_chunk = np.ones(480, dtype=np.float32)
    with patch.object(recorder.vad, "is_speech", return_value=True):
        assert recorder._is_speech(pcm_chunk) is True


# 🎙️ Test: Recording stops after silence is detected
@patch("chat_ui.voice_recorder.sd.InputStream")
@patch.object(VoiceRecorder, "_is_speech", return_value=False)
def test_record_until_silence(mock_is_speech, mock_stream, recorder):
    recorder.recording = True
    for _ in range(3):
        recorder.audio_queue.put(np.zeros(recorder.block_size, dtype=np.float32))

    fake_time = itertools.count(start=0, step=2)  # increments by 2s
    with patch("time.time", side_effect=lambda: next(fake_time)):
        audio = recorder._record_until_silence()

    assert isinstance(audio, np.ndarray)
    assert audio.size > 0


# 🧠 Test: Mocked transcription returns concatenated text
def test_transcribe_mocked(recorder):
    dummy_audio = np.zeros(16000, dtype=np.float32)
    recorder.model = MagicMock()
    recorder.model.transcribe.return_value = (
        [MagicMock(text="hello"), MagicMock(text="world")],
        None
    )
    result = recorder._transcribe(dummy_audio)
    assert result == "hello world"


# 🔄 Test: Voice command triggers persona switching
@patch("chat_ui.voice_recorder.PersonaService.select_persona")
@patch.object(VoiceRecorder, "_record_until_silence")
def test_voice_command_triggers_persona_switch(mock_record, mock_select, recorder):
    """Simulate recognized 'switch to Gwen' voice command triggers persona switch."""
    recorder.recording = True
    recorder.model = MagicMock()
    recorder.model.transcribe.return_value = ([MagicMock(text="switch to Gwen")], None)

    mock_record.side_effect = lambda: np.ones(160, dtype=np.float32)

    def stop_after_first_call(*args, **kwargs):
        recorder.recording = False  # ✅ stops loop after first persona switch

    mock_select.side_effect = stop_after_first_call

    thread = threading.Thread(target=recorder._run_loop, args=(lambda _: None,), daemon=True)
    thread.start()
    thread.join(timeout=2)

    mock_select.assert_called_once_with("gwen")

# ⚠️ Test: Silent loops auto-stop
@patch.object(VoiceRecorder, "_record_until_silence")
def test_silent_loops_trigger_auto_stop(mock_record, recorder):
    """Ensures silent transcription loops trigger auto-stop behavior."""
    recorder.recording = True
    recorder.max_empty_loops = 2
    recorder.model = MagicMock()
    recorder.model.transcribe.return_value = ([], None)

    # Provide dummy audio each loop
    mock_record.side_effect = lambda: np.ones(160, dtype=np.float32)

    status_updates = []

    def status_cb(msg):
        status_updates.append(msg)

    recorder.status_callback = status_cb

    thread = threading.Thread(target=recorder._run_loop, args=(lambda _: None,), daemon=True)
    thread.start()
    time.sleep(0.2)  # let the loop run a bit
    recorder.recording = False
    thread.join(timeout=2)

    assert any("Stopped" in msg for msg in status_updates)


# ▶️ Test: start_recording_async launches a thread
def test_start_recording_async_starts_thread(recorder):
    with patch.object(threading, "Thread", wraps=threading.Thread) as mock_thread:
        recorder.start_recording_async(callback=lambda _: None)
        assert recorder.recording is True
        assert mock_thread.called


# ⏹️ Test: stop sets recording to False
def test_stop_sets_recording_false(recorder):
    recorder.recording = True
    recorder.stop()
    assert recorder.recording is False

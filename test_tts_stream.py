import os
import tempfile
import requests
import io
import numpy as np
import sounddevice as sd

# === Set ffmpeg env paths ===
ffmpeg_dir = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_dir
os.environ["FFMPEG_BINARY"] = os.path.join(ffmpeg_dir, "ffmpeg.exe")
os.environ["FFPROBE_BINARY"] = os.path.join(ffmpeg_dir, "ffprobe.exe")

from pydub import AudioSegment

# === Config ===
url = "http://localhost:8000/chat/speak"
payload = {
    "user_id": "daniel",
    "message": "What is todays weather in New York?",
    "mode": "safe"
}

# === Stream request ===
with requests.post(url, json=payload, stream=True) as response:
    response.raise_for_status()
    buffer = io.BytesIO()

    for chunk in response.iter_content(chunk_size=4096):
        buffer.write(chunk)

    buffer.seek(0)
    audio = AudioSegment.from_file(buffer, format="mp3")
    audio = audio - 10  # reduce volume (optional)

    # Convert to NumPy array for playback
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples /= np.iinfo(audio.array_type).max  # normalize to [-1.0, 1.0]

    # Handle stereo/mono
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))

    sd.play(samples, samplerate=audio.frame_rate)
    sd.wait()

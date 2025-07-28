import os
import io
import requests
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
import shutil

# 🔧 Full path to ffmpeg folder
ffmpeg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ffmpeg", "bin"))
os.environ["PATH"] += os.pathsep + ffmpeg_dir
os.environ["FFMPEG_BINARY"] = os.path.join(ffmpeg_dir, "ffmpeg.exe")
os.environ["FFPROBE_BINARY"] = os.path.join(ffmpeg_dir, "ffprobe.exe")

# 🔒 Verify and assign converter
ffmpeg_path = os.environ["FFMPEG_BINARY"]
if not os.path.isfile(ffmpeg_path):
    raise FileNotFoundError(f"FFMPEG binary not found at: {ffmpeg_path}")
AudioSegment.converter = ffmpeg_path

print("🔧 FFMPEG_BINARY =", ffmpeg_path)


class VoicePlayer:
    def play_reply(self, text: str, on_start=None):
        """Stream already-generated reply through TTS playback."""
        try:
            print("🎤 [VoicePlayer] Sending TTS for known reply...")

            url = "http://localhost:8000/chat/speak-from-text"
            payload = { "reply": text }

            with requests.post(url, json=payload, stream=True) as response:
                print("✅ [VoicePlayer] Received TTS stream...")
                response.raise_for_status()

                buffer = io.BytesIO()
                for chunk in response.iter_content(chunk_size=4096):
                    buffer.write(chunk)

                buffer.seek(0)
                print("📦 [VoicePlayer] Buffer size:", buffer.getbuffer().nbytes)

                audio = AudioSegment.from_file(buffer, format="mp3")
                print("🎧 [VoicePlayer] Loaded MP3 | Duration:", len(audio), "ms | Channels:", audio.channels)

                audio = audio - 10  # optional volume reduction

                samples = np.array(audio.get_array_of_samples()).astype(np.float32)
                samples /= np.iinfo(audio.array_type).max

                if audio.channels == 2:
                    samples = samples.reshape((-1, 2))

                print("🔊 [VoicePlayer] Playing audio now...")
                if on_start:
                    on_start()  # 👈 show bubble when playback starts
                sd.play(samples, samplerate=audio.frame_rate)
                sd.wait()
                print("✅ [VoicePlayer] Playback finished")

        except Exception as e:
            print("❌ Voice playback error:", str(e))

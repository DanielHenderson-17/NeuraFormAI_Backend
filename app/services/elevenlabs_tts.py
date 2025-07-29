from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv
from pathlib import Path
from app.services.chat_engine import ChatEngine
from .text_cleaner import sanitize_for_speech

# Load environment variables (only need API key now)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=API_KEY)

def synthesize_reply_as_stream(text: str, voice_id: str = None):
    """
    Stream TTS audio for a given text. If no voice_id is provided,
    automatically retrieves it from the currently active persona
    using ChatEngine (single source of truth).
    """
    if not voice_id:
        voice_id = ChatEngine.get_voice_id()
        print(f"🎙️ No voice_id provided. Using persona voice: {voice_id}")

    cleaned_text = sanitize_for_speech(text)

    return client.text_to_speech.stream(
        voice_id=voice_id,
        model_id="eleven_monolingual_v1",
        text=cleaned_text,
    )

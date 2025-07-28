from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv
from pathlib import Path
from .text_cleaner import sanitize_for_speech

# Force loading from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print("API KEY LOADED:", os.getenv("ELEVENLABS_API_KEY"))

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
API_KEY = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(api_key=API_KEY)

def synthesize_reply_as_stream(text: str):
    cleaned_text = sanitize_for_speech(text)
    return client.text_to_speech.stream(
        voice_id=VOICE_ID,
        model_id="eleven_monolingual_v1",
        text=cleaned_text,
    )

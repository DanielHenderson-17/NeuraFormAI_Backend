import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load API key from .env
load_dotenv()
api_key = os.getenv("ELEVEN_API_KEY")

# Create client
client = ElevenLabs(api_key=api_key)

# Generate speech as a stream of audio chunks
stream = client.text_to_speech.convert(
    voice_id="JH3fX8OSjg6sNdEtPjxr",
    model_id="eleven_multilingual_v2",
    text="Hey Daniel, your ElevenLabs voice is live and ready to go!",
    output_format="mp3_44100"
)

# Save stream to file
with open("test_output.mp3", "wb") as f:
    for chunk in stream:
        f.write(chunk)

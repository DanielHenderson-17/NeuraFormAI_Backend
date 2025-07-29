import httpx
import os
from dotenv import load_dotenv
from app.helpers.persona_loader import load_persona

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api")
MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-3.5-turbo")
PERSONA_PATH = os.getenv("PERSONA_PATH", "app/config/characters/default_persona.yml")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "NeuraFormAI",
}

class ChatEngine:
    _persona_cache = {}  # { "default": { "messages": [...], "voice_id": str, "last_loaded": timestamp } }

    @staticmethod
    def _load_persona_if_needed():
        """Load and cache persona data, auto-refresh if YAML changes."""
        cache_key = "default"
        mtime = os.path.getmtime(PERSONA_PATH)

        if (cache_key not in ChatEngine._persona_cache or
            ChatEngine._persona_cache[cache_key]["last_loaded"] < mtime):
            persona_data = load_persona(PERSONA_PATH)
            ChatEngine._persona_cache[cache_key] = {
                "messages": persona_data["messages"],
                "voice_id": persona_data["voice_id"],
                "last_loaded": mtime,
            }
        else:
            print("✅ Using cached persona")

    @staticmethod
    def _get_persona():
        """Return cached persona messages and voice ID."""
        ChatEngine._load_persona_if_needed()
        cached = ChatEngine._persona_cache["default"]
        return {
            "messages": cached["messages"].copy(),
            "voice_id": cached["voice_id"],
        }

    @staticmethod
    def get_voice_id() -> str:
        """Public method to get current persona's voice ID."""
        ChatEngine._load_persona_if_needed()
        return ChatEngine._persona_cache["default"]["voice_id"]

    @staticmethod
    async def generate_reply(user_id: str, message: str, mode: str) -> dict:
        if mode == "safe":
            return await ChatEngine._use_openrouter(message)
        else:
            return {
                "reply": "Unfiltered mode not implemented yet.",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "voice_id": None,
            }

    @staticmethod
    async def _use_openrouter(message: str) -> dict:
        persona = ChatEngine._get_persona()
        messages = persona["messages"]
        voice_id = persona["voice_id"]

        messages.append({"role": "user", "content": message})

        for m in messages:
            print(f"{m['role'].upper()}: {m['content']}\n")

        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.8,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/chat/completions",
                headers=HEADERS,
                json=payload,
            )

            response.raise_for_status()
            result = response.json()
            reply = result["choices"][0]["message"]["content"].strip()
            usage = result.get("usage", {})

            return {
                "reply": reply,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "voice_id": voice_id,
            }

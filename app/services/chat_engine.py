import httpx
import os
from dotenv import load_dotenv
from app.helpers.persona_loader import load_persona
from app.services.persona_manager import PersonaManager

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api")
MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-3.5-turbo")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "NeuraPalAI",
}

class ChatEngine:
    _persona_cache = {}  # { user_id: { "messages": [...], "voice_id": str, "last_loaded": timestamp } }

    # === Private methods to manage persona loading and caching ===
    @staticmethod
    def _load_persona_if_needed(user_id: str):
        """Load and cache persona data for this user."""
        persona_path = PersonaManager.get_active_path(user_id)
        mtime = os.path.getmtime(persona_path)

        if (
            user_id not in ChatEngine._persona_cache
            or ChatEngine._persona_cache[user_id]["last_loaded"] < mtime
        ):
            persona_data = load_persona(persona_path)
            ChatEngine._persona_cache[user_id] = {
                "messages": persona_data["messages"],
                "voice_id": persona_data["voice_id"],
                "last_loaded": mtime,
            }
            print(f"🔄 Persona loaded for user {user_id} -> {os.path.basename(persona_path)}")
        else:
            print(f"✅ Using cached persona for user {user_id}")

    # === Get persona data and voice ID ===
    @staticmethod
    def _get_persona(user_id: str):
        ChatEngine._load_persona_if_needed(user_id)
        cached = ChatEngine._persona_cache[user_id]
        return {
            "messages": cached["messages"].copy(),
            "voice_id": cached["voice_id"],
        }

    # === Public methods for chat operations ===
    @staticmethod
    def get_voice_id(user_id: str) -> str:
        ChatEngine._load_persona_if_needed(user_id)
        return ChatEngine._persona_cache[user_id]["voice_id"]

    # === Context management ===
    @staticmethod
    def clear_context(user_id: str):
        """Completely clears conversation cache for a user."""
        if user_id in ChatEngine._persona_cache:
            del ChatEngine._persona_cache[user_id]
            print(f"🧹 Cleared and invalidated persona cache for user {user_id}")

    # === Persona management ===
    @staticmethod
    def preload_persona(user_id: str):
        """
        Force-loads persona messages/voice after switching personas.
        """
        ChatEngine._load_persona_if_needed(user_id)
        print(f"⚡ Preloaded persona for user {user_id}")

    # === Chat operations ===
    @staticmethod
    async def generate_reply(user_id: str, message: str, mode: str) -> dict:
        if mode == "safe":
            return await ChatEngine._use_openrouter(user_id, message)
        else:
            return {
                "reply": "Unfiltered mode not implemented yet.",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "voice_id": None,
            }

    # === OpenRouter API interaction ===
    @staticmethod
    async def _use_openrouter(user_id: str, message: str) -> dict:
        persona = ChatEngine._get_persona(user_id)
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

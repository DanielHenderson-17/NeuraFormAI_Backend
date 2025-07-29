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
    _persona_cache = {}  # { "default": { "messages": [...], "last_loaded": timestamp } }

    @staticmethod
    def _get_persona():
        """
        Load and cache the persona.
        Auto-refreshes if the YAML file changes.
        For now, a single global persona is used.
        """
        cache_key = "default"
        mtime = os.path.getmtime(PERSONA_PATH)

        if (cache_key not in ChatEngine._persona_cache or
            ChatEngine._persona_cache[cache_key]["last_loaded"] < mtime):
            print("🔄 Loading persona from YAML...")
            persona_messages = load_persona(PERSONA_PATH)
            ChatEngine._persona_cache[cache_key] = {
                "messages": persona_messages,
                "last_loaded": mtime,
            }
        else:
            print("✅ Using cached persona")

        # Return a copy to avoid mutating the cached messages
        return ChatEngine._persona_cache[cache_key]["messages"].copy()

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
            }

    @staticmethod
    async def _use_openrouter(message: str) -> dict:
        messages = ChatEngine._get_persona()
        messages.append({"role": "user", "content": message})

        print("=== Final Messages Sent ===")
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

            print("STATUS:", response.status_code)
            print("RESPONSE TEXT:", response.text)

            response.raise_for_status()
            result = response.json()
            reply = result["choices"][0]["message"]["content"].strip()
            usage = result.get("usage", {})
            return {
                "reply": reply,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }

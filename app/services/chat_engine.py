from pyexpat.errors import messages
import httpx
import os
from dotenv import load_dotenv
from app.helpers.persona_loader import load_persona  # ✅ Load from YAML

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api")
MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-3.5-turbo")
PERSONA_PATH = os.getenv("PERSONA_PATH", "app/config/characters/default_persona.yml")  # ✅ Generic default

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",  # Helps with OpenRouter tracking
    "X-Title": "NeuraFormAI",            # Optional but useful
}


class ChatEngine:
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
        # ✅ Load persona messages from YAML
        messages = load_persona(PERSONA_PATH)
        messages.append({"role": "user", "content": message})

        # ✅ Debug output
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

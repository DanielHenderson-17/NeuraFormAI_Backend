import uuid
import requests

class SessionManager:
    """
    Handles temporary user ID generation for persona requests.
    This simulates a real user system until authentication is added.
    """
    _user_id = None

    @classmethod
    def get_user_id(cls):
        if cls._user_id is None:
            cls._user_id = str(uuid.uuid4())
            print("🆔 [SessionManager] Generated Frontend User ID:", cls._user_id)
        else:
            print("🆔 [SessionManager] Using Existing Frontend User ID:", cls._user_id)
        return cls._user_id


class PersonaService:
    """
    Handles fetching and selecting personas from the backend API.
    """

    BASE_URL = "http://127.0.0.1:8000/api/personas"
    chat_window = None  # Registered global reference

    @classmethod
    def register_chat_window(cls, chat_window):
        """Registers chat_window instance for auto-greeting."""
        cls.chat_window = chat_window

    @classmethod
    def list_personas(cls):
        """Fetches all available personas from the backend."""
        try:
            print("🔎 [PersonaService] Fetching persona list...")
            response = requests.get(f"{cls.BASE_URL}/list")
            print(f"🔎 [PersonaService] Status: {response.status_code}")
            print(f"🔎 [PersonaService] Response: {response.text}")
            response.raise_for_status()
            return response.json().get("personas", [])
        except Exception as e:
            print(f"❌ [PersonaService] Failed to fetch persona list: {e}")
            return []

    @classmethod
    def get_active_persona(cls):
        """Gets the active persona for this user."""
        try:
            user_id = SessionManager.get_user_id()
            print(f"🔎 [PersonaService] Fetching active persona for user_id={user_id}")
            payload = {"user_id": user_id}
            response = requests.post(f"{cls.BASE_URL}/active", json=payload)
            print(f"🔎 [PersonaService] Status: {response.status_code}")
            print(f"🔎 [PersonaService] Response: {response.text}")
            response.raise_for_status()
            return response.json().get("active_persona", {})
        except Exception as e:
            print(f"❌ [PersonaService] Failed to fetch active persona: {e}")
            return {}

    @classmethod
    def select_persona(cls, persona_name: str):
        """Sets a new active persona for this user and triggers a hidden auto-greeting."""
        try:
            user_id = SessionManager.get_user_id()
            print(f"🛠️ [PersonaService] Selecting persona '{persona_name}' for user_id={user_id}")
            payload = {"user_id": user_id, "persona_name": persona_name}
            response = requests.post(f"{cls.BASE_URL}/select", json=payload)
            print(f"🛠️ [PersonaService] Status: {response.status_code}")
            print(f"🛠️ [PersonaService] Response: {response.text}")
            response.raise_for_status()
            active_persona = response.json().get("active_persona", {})

            # === Hidden auto-greeting ===
            if cls.chat_window:
                from PyQt6.QtCore import QCoreApplication
                from chat_ui.right.chat_window import AutoGreetingEvent

                message = "Introduce yourself briefly as the new persona."
                print(f"🤖 [PersonaService] Auto-sending hidden greeting message: {message}")
                QCoreApplication.postEvent(cls.chat_window, AutoGreetingEvent(message))

            return active_persona

        except Exception as e:
            print(f"❌ [PersonaService] Failed to select persona: {e}")
            return {}

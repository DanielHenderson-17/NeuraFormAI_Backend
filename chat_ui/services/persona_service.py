import uuid
import requests
import os

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
    Handles fetching and selecting personas from the backend API,
    including VRM loading and locked persona checks.
    """

    BASE_URL = "http://127.0.0.1:8000/api/personas"
    VRM_DIR = os.path.join("chat_ui", "assets", "vrms")
    chat_window = None
    vrm_container = None

    @classmethod
    def register_chat_window(cls, chat_window):
        """Registers chat_window instance for auto-greeting."""
        cls.chat_window = chat_window

    @classmethod
    def register_vrm_container(cls, vrm_container):
        """Registers the VRM container to display models."""
        cls.vrm_container = vrm_container

    @classmethod
    def list_personas(cls):
        """Fetches all available personas from the backend."""
        try:
            print("🔎 [PersonaService] Fetching persona list...")
            response = requests.get(f"{cls.BASE_URL}/list")
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
            payload = {"user_id": user_id}
            response = requests.post(f"{cls.BASE_URL}/active", json=payload)
            response.raise_for_status()
            return response.json().get("active_persona", {})
        except Exception as e:
            print(f"❌ [PersonaService] Failed to fetch active persona: {e}")
            return {}

    @classmethod
    def select_persona(cls, persona_name: str):
        """
        Sets a new active persona for this user, triggers auto-greeting,
        and handles VRM model loading.
        """
        try:
            user_id = SessionManager.get_user_id()
            print(f"🛠️ [PersonaService] Selecting persona '{persona_name}' for user_id={user_id}")
            payload = {"user_id": user_id, "persona_name": persona_name}
            response = requests.post(f"{cls.BASE_URL}/select", json=payload)
            response.raise_for_status()
            active_persona = response.json().get("active_persona", {})

            vrm_model = active_persona.get("vrm_model", "")
            locked = active_persona.get("locked", False)

            if locked:
                print(f"🔒 Persona '{persona_name}' is locked. VRM will not load.")
            else:
                vrm_path = os.path.join(cls.VRM_DIR, vrm_model)
                if os.path.exists(vrm_path):
                    print(f"✅ Loading VRM model for {persona_name}: {vrm_path}")
                    if cls.vrm_container:
                        cls.vrm_container.load_vrm(vrm_path)
                else:
                    print(f"⚠️ VRM file missing: {vrm_path}")

            # === Hidden auto-greeting ===
            if cls.chat_window:
                from PyQt6.QtCore import QCoreApplication
                from chat_ui.right.chat_window import AutoGreetingEvent

                message = "Introduce yourself briefly as the new persona."
                QCoreApplication.postEvent(cls.chat_window, AutoGreetingEvent(message))

            return active_persona

        except Exception as e:
            print(f"❌ [PersonaService] Failed to select persona: {e}")
            return {}

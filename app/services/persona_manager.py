from pathlib import Path
from app.helpers.persona_loader import load_persona_metadata

class PersonaManager:
    """
    Handles listing personas and managing the active persona per user.
    Future-proof: includes VRM model support.
    """

    _active_personas = {}  # { user_id: "persona.yml" }
    _characters_dir = Path("app/config/characters")

    # === List all available personas ===
    @classmethod
    def list_personas(cls) -> list[dict]:
        """
        Returns all available personas with metadata.
        [
            { "name": "Fuka", "file": "fuka.yml", "voice_id": "...", "vrm_model": None },
            ...
        ]
        """
        personas = []
        for file in cls._characters_dir.glob("*.yml"):
            meta = load_persona_metadata(file)
            personas.append({
                "name": meta["name"],
                "file": file.name,
                "voice_id": meta["voice_id"],
                "vrm_model": meta["vrm_model"],
                "locked": meta.get("locked", False),
                "validation_token": meta.get("validation_token", ""),
            })
        return personas
    
    # === Set the active persona for a user ===
    @classmethod
    def set_persona(cls, user_id: str, persona_name: str) -> None:
        """
        Sets the active persona for a given user.
        Validates persona exists before switching.
        """
        # Find matching persona file
        matches = [p for p in cls.list_personas() if p["name"].lower() == persona_name.lower()]
        if not matches:
            raise ValueError(f"Persona '{persona_name}' not found")

        selected_file = matches[0]["file"]
        cls._active_personas[user_id] = selected_file
        print(f"🔄 Persona for user {user_id} switched to {selected_file}")

    # === Get the active persona file path for a user ===
    @classmethod
    def get_active_path(cls, user_id: str) -> str:
        """
        Returns the full file path for the active persona of the given user.
        Defaults to default_persona.yml if none selected.
        """
        active_file = cls._active_personas.get(user_id)
    
        if not active_file:
            # Fallback to default_persona.yml
            default_file = "default_persona.yml"
            default_path = cls._characters_dir / default_file
            if default_path.exists():
                cls._active_personas[user_id] = default_file
                return str(default_path)
    
            # If default missing, pick first persona
            personas = cls.list_personas()
            if not personas:
                raise FileNotFoundError("No personas available")
            default = personas[0]["file"]
            cls._active_personas[user_id] = default
            return str(cls._characters_dir / default)
    
        return str(cls._characters_dir / active_file)

    # === Get metadata for the active persona of a user ===
    @classmethod
    def get_active_metadata(cls, user_id: str) -> dict:
        """
        Returns metadata for the active persona of a given user.
        If no persona is set, defaults to default_persona.yml.
        """
        active_file = cls._active_personas.get(user_id)

        # If no active persona, force default
        if not active_file:
            default_file = "default_persona.yml"
            default_path = cls._characters_dir / default_file

            if default_path.exists():
                cls._active_personas[user_id] = default_file
                from app.helpers.persona_loader import load_persona_metadata
                meta = load_persona_metadata(default_path)
                return {
                    "name": meta["name"],
                    "file": default_file,
                    "voice_id": meta["voice_id"],
                    "vrm_model": meta["vrm_model"],
                    "locked": meta.get("locked", False),
                    "validation_token": meta.get("validation_token", ""),
                }
            else:
                # If somehow default is missing, fall back to first available
                personas = cls.list_personas()
                if not personas:
                    return {}
                default = personas[0]
                cls._active_personas[user_id] = default["file"]
                return default

        # Already set persona
        from app.helpers.persona_loader import load_persona_metadata
        full_path = cls._characters_dir / active_file
        meta = load_persona_metadata(full_path)
        return {
            "name": meta["name"],
            "file": active_file,
            "voice_id": meta["voice_id"],
            "vrm_model": meta["vrm_model"],
            "locked": meta.get("locked", False),
            "validation_token": meta.get("validation_token", ""),
        }



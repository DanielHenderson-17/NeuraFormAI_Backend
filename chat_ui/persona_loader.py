import yaml
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
PERSONA_PATH = os.getenv("PERSONA_PATH", "app/config/characters/default_persona.yml")


def get_persona_name(path: str = PERSONA_PATH) -> str:
    try:
        with open(Path(path), "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("name", "Assistant")
    except Exception:
        return "Assistant"
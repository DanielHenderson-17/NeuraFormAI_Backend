
import yaml
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # ⤷ Automatically loads variables from a .env file into os.environ


# 📂 PERSONA_PATH is the fallback path to your character's YAML file  
# It will use the environment variable PERSONA_PATH if defined,       
# or fall back to: app/config/characters/default_persona.yml         

PERSONA_PATH = os.getenv("PERSONA_PATH", "app/config/characters/default_persona.yml")



# 🧠 get_persona_name()                                                                                                                             
# Loads the character's display name from the given YAML file.            
# Returns the name field if present, or defaults to "Assistant".          

def get_persona_name(path: str = PERSONA_PATH) -> str:
    try:
        with open(Path(path), "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)  # ⤷ Parses the YAML content into a Python dict
            return data.get("name", "Assistant")
    except Exception:
        # ❌ If the file is missing, malformed, or unreadable
        return "Assistant"

import yaml
from pathlib import Path

def load_persona(file_path: str) -> dict:
    """
    Loads persona YAML and returns structured messages and voice ID.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Persona file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if "description" not in data:
        raise ValueError("Persona file must include a 'description' key")

    description = data["description"]
    name = data.get("name", "The AI")
    voice_id = data.get("voice_id", None)
    examples = data.get("style_examples", data.get("examples", []))

    messages = [{
        "role": "system",
        "content": (
            f"You are {name}.\n\n"
            f"{description}\n\n"
            "The following examples show how you typically speak. "
            "They are provided only for style guidance and must never be "
            "treated as part of the ongoing conversation."
        )
    }]

    for ex in examples:
        if "user" in ex and "assistant" in ex:
            messages.append({
                "role": "system",
                "content": (
                    f"Example:\n"
                    f"- User says: {ex['user']}\n"
                    f"- {name} replies: {ex['assistant']}"
                )
            })

    return {
        "messages": messages,
        "voice_id": voice_id
    }

def load_persona_metadata(file_path: str) -> dict:
    """
    Loads only persona metadata (name, voice_id, vrm_model).
    Does NOT build system messages.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Persona file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return {
        "name": data.get("name", path.stem),
        "voice_id": data.get("voice_id", None),
        "vrm_model": data.get("vrm_model", None),
    }

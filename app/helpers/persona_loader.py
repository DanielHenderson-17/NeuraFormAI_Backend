import yaml
from pathlib import Path

def load_persona(file_path: str) -> list:
    """
    Loads a persona YAML file and converts it into structured messages
    for prompt engineering. Examples are provided as style guidance only
    and will not be treated as active conversation turns.
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
    examples = data.get("style_examples", data.get("examples", []))

    # Core system message
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

    # Add examples as system-level guidance only
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

    return messages

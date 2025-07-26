import yaml
from pathlib import Path

def load_persona(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Persona file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if "description" not in data:
        raise ValueError("Persona file must include a 'description' key")

    description = data["description"]
    examples = data.get("examples", [])

    messages = [{"role": "system", "content": description}]

    for ex in examples:
        if "user" in ex and "assistant" in ex:
            messages.append({"role": "user", "content": ex["user"]})
            messages.append({"role": "assistant", "content": ex["assistant"]})

    return messages

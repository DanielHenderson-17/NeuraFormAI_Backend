import re

UNWANTED_CHARS = set("~`^*_{}[]<>|\\#")

# === Sanitize text for speech synthesis by removing unwanted characters ===
def sanitize_for_speech(text: str) -> str:
    cleaned = ''.join(c for c in text if c not in UNWANTED_CHARS)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned

import re

UNWANTED_CHARS = set("~`^*_{}[]<>|\\#")

def sanitize_for_speech(text: str) -> str:
    # Remove unwanted characters
    cleaned = ''.join(c for c in text if c not in UNWANTED_CHARS)
    
    # Optionally collapse multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned

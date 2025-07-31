import httpx

API_URL = "https://openrouter.ai/api/v1/models"

# === List available OpenRouter models ===
def list_models():
    try:
        response = httpx.get(API_URL)
        response.raise_for_status()
        data = response.json()
        print("Available OpenRouter Models:\n")
        for model in data["data"]:
            print(f"- {model['id']}")
    except Exception as e:
        print(f"Failed to fetch models: {e}")

if __name__ == "__main__":
    list_models()

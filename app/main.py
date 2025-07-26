from fastapi import FastAPI
from app.api import chat
import asyncio
from app.services.openrouter_credits import get_openrouter_credits

app = FastAPI(
    title="NeuraFormAI",
    description="Modular AI Companion Backend",
    version="0.1.0",
)

# Mount chat-related routes
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.on_event("startup")
async def log_openrouter_credits():
    try:
        credits = await get_openrouter_credits()
        print("✅ OpenRouter Credits:")
        print(credits)
    except Exception as e:
        print("❌ Failed to fetch OpenRouter credits:", str(e))

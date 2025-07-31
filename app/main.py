from fastapi import FastAPI
from app.api import chat, personas 
import asyncio
from app.services.openrouter_credits import get_openrouter_credits

app = FastAPI(
    title="NeuraPalAI",
    description="Modular AI Companion Backend",
    version="0.1.0",
)

# === Include CORS middleware ===
from fastapi.middleware.cors import CORSMiddleware
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# === Include routers for chat and personas ===
app.include_router(personas.router, prefix="/api")

@app.on_event("startup")
async def log_openrouter_credits():
    try:
        credits = await get_openrouter_credits()
        print("✅ OpenRouter Credits:")
        print(credits)
    except Exception as e:
        print("❌ Failed to fetch OpenRouter credits:", str(e))

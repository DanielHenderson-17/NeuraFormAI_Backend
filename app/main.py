from fastapi import FastAPI
from app.api import chat, personas
from app.api.auth import router as auth_router
import asyncio
from app.services.openrouter_credits import get_openrouter_credits
from app.config.database import init_database, cleanup_database

app = FastAPI(
    title="NeuraPalAI",
    description="Modular AI Companion Backend",
    version="0.1.0",
)

# === Include CORS middleware ===
from fastapi.middleware.cors import CORSMiddleware

# CORS (development-friendly defaults; tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# === Include routers for chat and personas ===
app.include_router(personas.router, prefix="/api")
app.include_router(auth_router)

@app.on_event("startup")
async def log_openrouter_credits():
    try:
        credits = await get_openrouter_credits()
        print("✅ OpenRouter Credits:")
        print(credits)
    except Exception as e:
        print("❌ Failed to fetch OpenRouter credits:", str(e))


@app.on_event("startup")
async def startup_database():
    await init_database()


@app.on_event("shutdown")
async def shutdown_database():
    await cleanup_database()

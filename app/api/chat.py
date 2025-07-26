from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_engine import ChatEngine

router = APIRouter()

# ✅ Request body schema
class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str  # "safe" or "unfiltered"

# ✅ Response body schema (now includes token usage)
class ChatResponse(BaseModel):
    reply: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

# ✅ Endpoint
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    result = await ChatEngine.generate_reply(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
    )
    return ChatResponse(**result)

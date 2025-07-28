from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.services.chat_engine import ChatEngine
from fastapi.responses import StreamingResponse
from app.services.elevenlabs_tts import synthesize_reply_as_stream

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

# ✅ Chat endpoint
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    result = await ChatEngine.generate_reply(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
    )
    return ChatResponse(**result)

# ✅ Speech synthesis using generated reply
@router.post("/speak")
async def chat_speak_endpoint(request: ChatRequest):
    result = await ChatEngine.generate_reply(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
    )
    audio_stream = synthesize_reply_as_stream(result["reply"])
    return StreamingResponse(
        content=audio_stream,
        media_type="audio/mpeg",
        status_code=200
    )

# ✅ NEW: Use existing reply directly (prevents mismatch)
@router.post("/speak-from-text")
def speak_from_text(reply: str = Body(..., embed=True)):
    audio_stream = synthesize_reply_as_stream(reply)
    return StreamingResponse(
        content=audio_stream,
        media_type="audio/mpeg",
        status_code=200
    )

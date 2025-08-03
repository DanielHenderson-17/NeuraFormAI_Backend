from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.services.chat_engine import ChatEngine
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.elevenlabs_tts import synthesize_reply_as_stream

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str
    voice_enabled: bool = True 

class ChatResponse(BaseModel):
    reply: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    voice_id: str | None = None 

# === Chat endpoint for generating replies ===
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(f"📩 [/chat/] message received from {request.user_id} | voice_enabled={request.voice_enabled}")
    result = await ChatEngine.generate_reply(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
    )
    return ChatResponse(**result)

# === Chat endpoint for streaming TTS audio ===
@router.post("/speak")
async def chat_speak_endpoint(request: ChatRequest):
    print(f"📡 [/chat/speak] Received TTS request | voice_enabled={request.voice_enabled}")

    result = await ChatEngine.generate_reply(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
    )

    if not request.voice_enabled:
        print("🔇 [BACKEND] voice_enabled is FALSE — skipping ElevenLabs.")
        return JSONResponse(
            content={"skipped": True, "reason": "voice disabled"},
            status_code=200
        )

    voice_id = result.get("voice_id")
    print(f"🗣️ Sending to ElevenLabs: \"{result['reply'][:60]}...\" | voice_id={voice_id}")
    audio_stream = synthesize_reply_as_stream(result["reply"], voice_id)
    return StreamingResponse(
        content=audio_stream,
        media_type="audio/mpeg",
        status_code=200
    )

# === Endpoint to convert text to speech using active persona ===
@router.post("/speak-from-text")
def speak_from_text(
    user_id: str = Body(..., embed=True),
    reply: str = Body(..., embed=True)
):
    """
    Converts a given reply text to speech using the active persona's voice.
    Requires both user_id and reply in the JSON body.
    """
    print(f"🎙️ [Backend] speak-from-text called for user_id={user_id}")
    print(f"📨 Payload: \"{reply[:60]}...\"")

    try:
        # Get persona voice via ChatEngine helper (per user session)
        voice_id = ChatEngine.get_voice_id(user_id)
        print(f"🗣️ Using voice_id={voice_id}")

        # Generate and stream audio
        print(f"🎙️ [Backend] Calling synthesize_reply_as_stream...")
        audio_stream = synthesize_reply_as_stream(reply, voice_id)
        print(f"🎙️ [Backend] Audio stream created, returning StreamingResponse...")
        
        return StreamingResponse(
            content=audio_stream,
            media_type="audio/mpeg",
            status_code=200
        )
    except Exception as e:
        print(f"❌ [Backend] Error in speak-from-text: {e}")
        import traceback
        traceback.print_exc()
        raise



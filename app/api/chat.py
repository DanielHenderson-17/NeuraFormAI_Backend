from fastapi import APIRouter, Body, Query, HTTPException
from pydantic import BaseModel
from app.services.chat_engine import ChatEngine
from app.services.conversation_service import ConversationService
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.elevenlabs_tts import synthesize_reply_as_stream
from typing import List, Dict, Any

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str
    voice_enabled: bool = True 
    save_to_history: bool = True 

class ChatResponse(BaseModel):
    reply: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    voice_id: str | None = None 

# === Chat endpoint for generating replies ===
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(f"📩 [/chat/] message received from {request.user_id} | voice_enabled={request.voice_enabled} | save_to_history={request.save_to_history}")
    result = await ChatEngine.generate_reply(
        user_id=request.user_id,
        message=request.message,
        mode=request.mode,
        save_to_history=request.save_to_history,
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

# === Endpoint to get conversation history ===
@router.get("/history")
async def get_conversation_history(
    user_id: str = Query(...),
    persona_name: str = Query(...)
):
    """
    Get conversation history for a user-persona pair.
    """
    print(f"📚 [Backend] get_conversation_history called for user_id={user_id}, persona_name={persona_name}")

    try:
        conv_service = ConversationService()
        conversation_id = await conv_service.get_or_create_conversation(user_id, persona_name)
        messages = await conv_service.get_conversation_messages(conversation_id)
        
        print(f"📚 [Backend] Found {len(messages)} messages in conversation history")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "messages": messages
        }
        
    except Exception as e:
        print(f"❌ [Backend] Error in get_conversation_history: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )


@router.get("/conversation-for-persona")
async def get_conversation_for_persona(
    user_id: str = Query(..., description="User ID"),
    persona_name: str = Query(..., description="Persona name")
):
    """Get conversation ID for a specific user-persona pair"""
    try:
        print(f"🔍 [Backend] Getting conversation for user_id={user_id}, persona={persona_name}")
        
        conversation_service = ConversationService()
        conversation_id = await conversation_service.get_conversation_for_persona(user_id, persona_name)
        
        if conversation_id:
            return JSONResponse(
                content={"success": True, "conversation_id": conversation_id},
                status_code=200
            )
        else:
            return JSONResponse(
                content={"success": False, "conversation_id": None, "message": "No conversation found"},
                status_code=404
            )
        
    except Exception as e:
        print(f"❌ [Backend] Error in get_conversation_for_persona: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )


# === Conversation Management Models ===
class UpdateConversationRequest(BaseModel):
    title: str

# === Conversation Management Endpoints ===

@router.get("/conversations")
async def get_conversations(user_id: str = Query(..., description="User ID")):
    """Get all conversations for a user"""
    try:
        print(f"📂 [Backend] Getting conversations for user_id={user_id}")
        
        conversation_service = ConversationService()
        conversations = await conversation_service.get_user_conversations(user_id)
        
        return JSONResponse(
            content={"success": True, "conversations": conversations},
            status_code=200
        )
        
    except Exception as e:
        print(f"❌ [Backend] Error in get_conversations: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )


@router.put("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, request: UpdateConversationRequest):
    """Update conversation title"""
    try:
        print(f"✏️ [Backend] Updating conversation {conversation_id} title to: {request.title}")
        
        conversation_service = ConversationService()
        success = await conversation_service.update_conversation_title(conversation_id, request.title)
        
        if success:
            return JSONResponse(
                content={"success": True, "message": "Conversation title updated"},
                status_code=200
            )
        else:
            return JSONResponse(
                content={"success": False, "error": "Conversation not found"},
                status_code=404
            )
            
    except Exception as e:
        print(f"❌ [Backend] Error in update_conversation: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and all its messages"""
    try:
        print(f"🗑️ [Backend] Deleting conversation {conversation_id}")
        
        conversation_service = ConversationService()
        success = await conversation_service.delete_conversation(conversation_id)
        
        if success:
            return JSONResponse(
                content={"success": True, "message": "Conversation deleted"},
                status_code=200
            )
        else:
            return JSONResponse(
                content={"success": False, "error": "Conversation not found"},
                status_code=404
            )
            
    except Exception as e:
        print(f"❌ [Backend] Error in delete_conversation: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500
        )



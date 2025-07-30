from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.persona_manager import PersonaManager

router = APIRouter(prefix="/personas", tags=["Personas"])

class PersonaSelectRequest(BaseModel):
    user_id: str
    persona_name: str

class ActivePersonaRequest(BaseModel):
    user_id: str

@router.get("/list")
def list_personas():
    personas = PersonaManager.list_personas()
    if not personas:
        raise HTTPException(status_code=404, detail="No personas found")
    return {"personas": personas}

@router.post("/select")
def select_persona(request: PersonaSelectRequest):
    """
    Switches the active persona for a given user.
    """
    try:
        PersonaManager.set_persona(request.user_id, request.persona_name)
        return {
            "message": f"Persona switched to '{request.persona_name}'",
            "active_persona": PersonaManager.get_active_metadata(request.user_id)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/active")
def get_active_persona(request: ActivePersonaRequest):
    """
    Returns the currently active persona for the given user.
    Automatically falls back to default_persona.yml if none selected.
    """
    active = PersonaManager.get_active_metadata(request.user_id)
    if not active:
        raise HTTPException(status_code=404, detail="No active persona found")
    return {"active_persona": active}

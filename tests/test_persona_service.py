import pytest
import uuid
from chat_ui.services.persona_service import SessionManager, PersonaService


# === Fixture to reset user ID before each test ===
@pytest.fixture(autouse=True)
def reset_user_id():
    SessionManager._user_id = None
    yield
    SessionManager._user_id = None


# === Test: SessionManager generates UUID ===
def test_session_manager_generates_uuid():
    first_id = SessionManager.get_user_id()
    second_id = SessionManager.get_user_id()

    assert first_id == second_id  # Should reuse same ID
    assert uuid.UUID(first_id)    # Should be valid UUID


# === Test: Listing personas ===
def test_list_personas(requests_mock):
    mock_data = {"personas": ["Fuka", "Gwen"]}
    requests_mock.get("http://127.0.0.1:8000/api/personas/list", json=mock_data)

    result = PersonaService.list_personas()
    assert result == ["Fuka", "Gwen"]


# === Test: Getting active persona ===
def test_get_active_persona(requests_mock):
    mock_persona = {"active_persona": {"name": "Fuka"}}
    requests_mock.post("http://127.0.0.1:8000/api/personas/active", json=mock_persona)

    result = PersonaService.get_active_persona()
    assert result["name"] == "Fuka"


# === Test: Selecting a persona ===
def test_select_persona(requests_mock):
    mock_persona = {"active_persona": {"name": "Gwen"}}
    requests_mock.post("http://127.0.0.1:8000/api/personas/select", json=mock_persona)

    result = PersonaService.select_persona("Gwen")
    assert result["name"] == "Gwen"

import pytest
from unittest.mock import mock_open, patch
from chat_ui.persona_loader import get_persona_name


# ✅ Test: YAML contains a valid "name" field
# Simulates loading a valid persona file with name: "Fuka"
def test_get_persona_name_success():
    mock_yaml = "name: Fuka\nage: 25"
    with patch("builtins.open", mock_open(read_data=mock_yaml)):
        with patch("chat_ui.persona_loader.yaml.safe_load", return_value={"name": "Fuka"}):
            result = get_persona_name("some/fake/path.yml")
            assert result == "Fuka"


# ❌ Test: File not found or unreadable
# Should fallback and return "Assistant"
def test_get_persona_name_fallback_on_exception():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = get_persona_name("nonexistent.yml")
        assert result == "Assistant"


# ⚠️ Test: YAML loads, but has no "name" field
# Should return the fallback value "Assistant"
def test_get_persona_name_missing_name_field():
    mock_yaml = "title: NoName"
    with patch("builtins.open", mock_open(read_data=mock_yaml)):
        with patch("chat_ui.persona_loader.yaml.safe_load", return_value={"title": "NoName"}):
            result = get_persona_name("some/fake/path.yml")
            assert result == "Assistant"

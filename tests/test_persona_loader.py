import pytest
from unittest.mock import mock_open, patch
from chat_ui.persona_loader import get_persona_name


# === Test: Successful persona name retrieval from YAML file ===
def test_get_persona_name_success():
    mock_yaml = "name: Fuka\nage: 25"
    with patch("builtins.open", mock_open(read_data=mock_yaml)):
        with patch("chat_ui.persona_loader.yaml.safe_load", return_value={"name": "Fuka"}):
            result = get_persona_name("some/fake/path.yml")
            assert result == "Fuka"


# === Test: Fallback to default name when YAML file is empty or missing ===
def test_get_persona_name_fallback_on_exception():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = get_persona_name("nonexistent.yml")
        assert result == "Assistant"


# === Test: Fallback to default name when 'name' field is missing in YAML ===
def test_get_persona_name_missing_name_field():
    mock_yaml = "title: NoName"
    with patch("builtins.open", mock_open(read_data=mock_yaml)):
        with patch("chat_ui.persona_loader.yaml.safe_load", return_value={"title": "NoName"}):
            result = get_persona_name("some/fake/path.yml")
            assert result == "Assistant"

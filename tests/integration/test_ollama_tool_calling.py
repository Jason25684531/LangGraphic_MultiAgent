import pytest
from studio.models.factory import create_chat_model
from studio.tools.example_tools import get_magic_number

pytestmark = pytest.mark.ollama


def test_ollama_calls_tool(ollama_settings):
    response = create_chat_model(ollama_settings).bind_tools([get_magic_number]).invoke("Call get_magic_number and nothing else.")
    assert response.tool_calls, "Model did not call get_magic_number"

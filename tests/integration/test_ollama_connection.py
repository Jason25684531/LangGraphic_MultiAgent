import pytest
from studio.models.factory import create_chat_model

pytestmark = pytest.mark.ollama


def test_ollama_connection(ollama_settings):
    assert create_chat_model(ollama_settings).invoke("Reply OK").content

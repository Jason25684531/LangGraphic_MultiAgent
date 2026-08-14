import pytest
from studio.agents.reviewer import ReviewResult
from studio.models.factory import create_chat_model

pytestmark = pytest.mark.ollama


def test_ollama_structured_output(ollama_settings):
    result = create_chat_model(ollama_settings).with_structured_output(ReviewResult).invoke("Return a pass review with brief feedback.")
    assert result.status in {"pass", "revise"}

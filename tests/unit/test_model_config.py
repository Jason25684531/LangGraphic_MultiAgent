from studio.config import StudioSettings


def test_defaults_and_environment(monkeypatch):
    assert StudioSettings().ollama_base_url == "http://127.0.0.1:11434"
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    assert StudioSettings().ollama_model == "test-model"

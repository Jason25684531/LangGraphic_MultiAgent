import urllib.request

import pytest

from studio.config import StudioSettings


@pytest.fixture(scope="session")
def ollama_settings():
    settings = StudioSettings()
    try:
        urllib.request.urlopen(settings.ollama_base_url + "/api/tags", timeout=2)
    except Exception:
        pytest.skip(f"Ollama unavailable at {settings.ollama_base_url}")
    return settings

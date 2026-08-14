import pytest
from studio.config import StudioSettings
from studio.models.factory import UnsupportedProviderError, create_chat_model


def test_factory_rejects_unknown_provider():
    with pytest.raises(UnsupportedProviderError): create_chat_model(StudioSettings(llm_provider="other"))

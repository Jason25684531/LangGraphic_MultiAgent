from .ollama import create_ollama_model


class UnsupportedProviderError(ValueError):
    pass


def create_chat_model(settings):
    if settings.llm_provider != "ollama":
        raise UnsupportedProviderError(f"Unsupported provider: {settings.llm_provider}")
    return create_ollama_model(settings)

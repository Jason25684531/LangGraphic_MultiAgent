from langchain_ollama import ChatOllama


def create_ollama_model(settings):
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=settings.ollama_temperature,
    )

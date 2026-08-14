from pydantic_settings import BaseSettings, SettingsConfigDict


class StudioSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    ollama_temperature: float = 0
    max_iterations: int = 3

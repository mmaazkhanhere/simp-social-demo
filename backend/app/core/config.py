from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SimpSocial Demo API"
    environment: str = "development"
    database_url: str = f"sqlite:///{(Path(__file__).resolve().parents[3] / 'backend' / 'app.db').as_posix()}"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    default_dealership_slug: str = "sunrise-auto"
    default_language: str = "english"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()


from pathlib import Path

from pydantic import field_validator
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

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_sqlite_path(cls, value: str) -> str:
        sqlite_prefix = "sqlite:///"
        if not isinstance(value, str) or not value.startswith(sqlite_prefix):
            return value

        db_path = value[len(sqlite_prefix) :]
        # Keep explicit absolute SQLite paths unchanged (unix and Windows drive forms).
        if db_path.startswith("/") or (len(db_path) > 1 and db_path[1] == ":"):
            return value

        backend_dir = Path(__file__).resolve().parents[2]
        repo_root = Path(__file__).resolve().parents[3]
        base_dir = repo_root if ("/" in db_path or "\\" in db_path) else backend_dir
        return f"{sqlite_prefix}{(base_dir / db_path).resolve().as_posix()}"


settings = Settings()

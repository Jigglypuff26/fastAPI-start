from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.env import ensure_env_file

ensure_env_file()


class Settings(BaseSettings):
    app_name: str = "FastAPI Project"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

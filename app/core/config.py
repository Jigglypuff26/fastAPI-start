from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.env import ensure_env_file

ensure_env_file()


class Settings(BaseSettings):
    app_name: str = "FastAPI Project"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]
    cors_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    cors_headers: list[str] = ["Authorization", "Content-Type"]
    # "testserver" is the fixed Host Starlette's TestClient sends; needed so
    # TrustedHostMiddleware doesn't reject requests made by the test suite.
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]
    # IP-адреса или подсети (CIDR), которым разрешён доступ. Пустой список —
    # ограничение отключено (доступ разрешён всем).
    allowed_ips: list[str] = []
    rate_limit: str = "100/minute"
    db_enabled: bool = True
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "postgres"
    redis_enabled: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

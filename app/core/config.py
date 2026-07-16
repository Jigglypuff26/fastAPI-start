from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.env import ensure_env_file

ensure_env_file()


class Settings(BaseSettings):
    # Название приложения — в заголовке FastAPI и в Swagger UI.
    app_name: str = "FastAPI Project"
    # Режим отладки: true включает /docs, /redoc, /openapi.json. В проде — false.
    debug: bool = False

    # Разрешённые источники (Origin) для CORS.
    cors_origins: list[str] = ["http://localhost:3000"]
    # Разрешённые HTTP-методы для CORS-запросов.
    cors_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    # Разрешённые заголовки запроса для CORS.
    cors_headers: list[str] = ["Authorization", "Content-Type"]

    # Хосты (заголовок Host), с которыми сервер согласится работать.
    # "testserver" — фиксированный Host, который отправляет TestClient из Starlette;
    # нужен, чтобы TrustedHostMiddleware не отклонял запросы из тестов.
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]
    # IP-адреса или подсети (CIDR), которым разрешён доступ. Пустой список —
    # ограничение отключено (доступ разрешён всем).
    allowed_ips: list[str] = []
    # Лимит запросов с одного IP, формат "<число>/<период>" (100/minute и т.п.).
    rate_limit: str = "100/minute"

    # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    log_level: str = "INFO"

    # Включает/выключает подключение к PostgreSQL (/api/v1/postgre-check).
    db_enabled: bool = True
    # Хост базы данных.
    db_host: str = "localhost"
    # Порт PostgreSQL.
    db_port: int = 5432
    # Имя пользователя для подключения к БД.
    db_username: str = "postgres"
    # Пароль пользователя БД.
    db_password: str = "postgres"
    # Название базы данных.
    db_name: str = "postgres"

    # Включает/выключает подключение к Redis (/api/v1/redis-check).
    redis_enabled: bool = True
    # Хост Redis.
    redis_host: str = "localhost"
    # Порт Redis.
    redis_port: int = 6379
    # Пароль Redis. Пусто — без аутентификации (только для локальной разработки).
    redis_password: str = ""
    # Номер логической базы Redis (0-15 по умолчанию).
    redis_db: int = 0
    # Максимальное число соединений в пуле Redis.
    redis_max_connections: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Размер пула соединений SQLAlchemy к PostgreSQL.
    db_pool_size: int = 10
    # Число дополнительных соединений сверх db_pool_size при пиковой нагрузке.
    db_max_overflow: int = 5

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

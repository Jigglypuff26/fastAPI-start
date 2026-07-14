import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core.config import settings
from app.models import Base

# Объект конфигурации Alembic — даёт доступ к значениям из используемого .ini-файла.
config = context.config

# Настройка логирования Python из конфига (по сути — регистрация логгеров).
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Строка подключения берётся из настроек приложения (.env), а не из alembic.ini,
# чтобы не дублировать и не рассинхронизировать креды в двух местах.
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata

# Прочие значения из конфига при необходимости можно получить так:
# my_important_option = config.get_main_option("my_important_option")
# и т.д.


def run_migrations_offline() -> None:
    """Запуск миграций в режиме 'offline'.

    Контекст настраивается только URL-строкой, без Engine (хотя Engine тоже
    допустим). Не создавая Engine, можно обойтись без установленного DBAPI-драйвера.

    Вызовы context.execute() в этом режиме выводят SQL-строки в stdout,
    а не выполняют их.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создаёт Engine и связывает соединение с контекстом миграций."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в режиме 'online'."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

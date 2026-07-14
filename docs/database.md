# 🗄️ База данных (PostgreSQL)

Подключение к PostgreSQL, переменные окружения и проверка соединения.

## ⚙️ Переменные окружения

Строка подключения собирается в [app/core/config.py](../app/core/config.py) (свойство `database_url`) из отдельных переменных `.env`:

| Переменная    | Описание                                   | Пример                             |
| ------------- | ------------------------------------------- | ----------------------------------- |
| `DB_ENABLED`  | Включает/выключает подключение к базе       | `true`                              |
| `DB_HOST`     | Хост базы данных                            | `localhost`                         |
| `DB_PORT`     | Порт PostgreSQL                             | `5432`                              |
| `DB_USERNAME` | Имя пользователя для подключения            | `postgres`                          |
| `DB_PASSWORD` | Пароль пользователя                         | —                                    |
| `DB_NAME`     | Название базы данных                        | `postgres`                          |
| `DB_POOL_SIZE`     | Размер пула соединений SQLAlchemy      | `10`                                |
| `DB_MAX_OVERFLOW`  | Доп. соединения сверх пула при пике    | `5`                                 |

Значения по умолчанию (для локальной разработки) заданы в [.env.example](../.env.example). Реальные значения — в `.env`, который не попадает в git (см. [docs/security.md](security.md#секреты-и-env)).

## 🔌 Подключение и пул соединений

[app/core/db.py](../app/core/db.py) создаёт один общий async `Engine` (SQLAlchemy 2.0, драйвер `asyncpg`) с пулом соединений (`DB_POOL_SIZE` + `DB_MAX_OVERFLOW`, `pool_pre_ping=True`) на весь процесс приложения — отдельные запросы не открывают новое TCP-соединение к Postgres, а берут его из пула.

`get_db()` — FastAPI-dependency, отдающая `AsyncSession` для использования в роутах:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db


@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)) -> list[str]:
    ...
```

Пул закрывается при остановке приложения (`lifespan` в [app/main.py](../app/main.py), `engine.dispose()`).

## 🧩 Модели и миграции

Модели ORM наследуются от `Base` из [app/models/base.py](../app/models/base.py) и располагаются в `app/models/`. Схема БД версионируется через Alembic — конфигурация в [migrations/env.py](../migrations/env.py) и [alembic.ini](../alembic.ini); подробнее о командах — в разделе [Миграции БД](../README.md#-миграции-бд-alembic) README.

## ✅ Проверка подключения

Эндпоинт `GET /postgre-check` пытается подключиться к базе (через пул) и выполнить `SELECT 1`:

- `{"message": "подключен к базе"}` — соединение установлено.
- `{"message": "не подключен к базе"}` — соединение не удалось (неверные креды, БД недоступна, база не существует и т.п.).
- `{"message": "проверка отключена (DB_ENABLED=false)"}` — `DB_ENABLED=false` в `.env`, попытка подключения не выполняется вовсе.

Реализация:

- [app/core/db.py](../app/core/db.py) — `check_postgres_connection()`, берёт соединение из пула через [SQLAlchemy](https://www.sqlalchemy.org/) (async engine, драйвер [asyncpg](https://github.com/MagicStack/asyncpg)) с таймаутом подключения 3 секунды, любую ошибку превращает в `False`.
- [app/routers/http/postgre.py](../app/routers/http/postgre.py) — сам роут.

## 💻 Запуск без Docker

Если PostgreSQL установлен на хост-машине и слушает `localhost:5432`, значения по умолчанию в `.env` (`DB_HOST=localhost`) работают без изменений:

```powershell
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/postgre-check
```

## 🐳 Запуск в Docker

Внутри контейнера `localhost` указывает на сам контейнер, а не на хост-машину, поэтому для БД, поднятой на хосте, `docker-compose.yml` переопределяет `DB_HOST=host.docker.internal` — подробности в [docs/docker.md](docker.md#подключение-к-postgres-на-хосте).

Если вместо этого Postgres должен запускаться как отдельный сервис в том же compose-стеке — подключите оверрайд [docker/docker-compose.postgres.yml](../docker/docker-compose.postgres.yml) (см. [docs/docker.md](docker.md#postgres)), он сам переопределяет `DB_HOST=db`.

## 🔍 Диагностика

Если `/postgre-check` возвращает «не подключен к базе»:

1. Проверить, что PostgreSQL действительно запущен и слушает указанный `DB_HOST:DB_PORT`.
2. Проверить `DB_USERNAME`/`DB_PASSWORD`/`DB_NAME` — опечатка в любом из них тоже даёт «не подключен».
3. Если приложение запущено в Docker — учесть сетевые особенности контейнера (см. раздел выше).

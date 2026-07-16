# ⚡ Redis

Подключение к Redis, переменные окружения и проверка соединения.

## Переменные окружения

Параметры подключения задаются в [app/core/config.py](../app/core/config.py) отдельными полями `Settings`, читаемыми из `.env`:

| Переменная       | Описание                                             | Пример      |
| ---------------- | ----------------------------------------------------- | ----------- |
| `REDIS_ENABLED`  | Включает/выключает подключение к Redis                | `true`      |
| `REDIS_HOST`     | Хост Redis                                            | `localhost` |
| `REDIS_PORT`     | Порт Redis                                            | `6379`      |
| `REDIS_PASSWORD` | Пароль (пусто — без аутентификации)                   | —           |
| `REDIS_DB`       | Номер логической базы Redis                           | `0`         |
| `REDIS_MAX_CONNECTIONS` | Максимум соединений в пуле Redis                | `20`        |

Значения по умолчанию (для локальной разработки) заданы в [.env.example](../.env.example). Реальные значения — в `.env`, который не попадает в git (см. [docs/security.md](security.md#секреты-и-env)).

## 🔌 Пул соединений

[app/core/redis_client.py](../app/core/redis_client.py) создаёт один общий `ConnectionPool` (`redis.asyncio`) на весь процесс приложения — `get_redis()` возвращает клиент, использующий этот пул, вместо того чтобы каждый запрос открывал новое TCP-соединение к Redis:

```python
from fastapi import Depends
from redis.asyncio import Redis

from app.core.redis_client import get_redis


@router.get("/cached")
async def cached(redis: Redis = Depends(get_redis)) -> dict[str, str | None]:
    return {"value": await redis.get("key")}
```

Пул закрывается при остановке приложения (`lifespan` в [app/main.py](../app/main.py), `redis_pool.disconnect()`).

## ✅ Проверка подключения

Эндпоинт `GET /api/v1/redis-check` пытается подключиться к Redis (через пул) и выполнить `PING`:

- `{"message": "подключен к redis"}` — соединение установлено.
- `{"message": "не подключен к redis"}` — соединение не удалось (неверные креды, Redis недоступен и т.п.).
- `{"message": "проверка отключена (REDIS_ENABLED=false)"}` — `REDIS_ENABLED=false` в `.env`, попытка подключения не выполняется вовсе.

Реализация:

- [app/core/redis_client.py](../app/core/redis_client.py) — `check_redis_connection()`, использует общий пул через [redis-py](https://github.com/redis/redis-py) (`redis.asyncio`) с таймаутом 3 секунды, любую ошибку подключения превращает в `False`.
- [app/routers/http/redis.py](../app/routers/http/redis.py) — сам роут.

## 🐳 Запуск Redis через Docker

Redis — опциональный сервис: базовый [docker/docker-compose.yml](../docker/docker-compose.yml) его не содержит, поэтому обычный `docker compose up` контейнер Redis не создаёт. Чтобы поднять Redis вместе с приложением, подключите оверрайд [docker/docker-compose.redis.yml](../docker/docker-compose.redis.yml) (образ `redis:7-alpine`, данные сохраняются в volume `redis-data`, порт `6379` проброшен на хост):

```powershell
docker compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml up --build
```

При таком запуске сервис `api` обращается к Redis по имени сервиса — `docker-compose.redis.yml` переопределяет `REDIS_HOST=redis` для `api` (аналогично тому, как `DB_HOST` переопределяется для Postgres, см. [docs/database.md](database.md)) и ждёт, пока Redis не станет healthy.

Подробнее о том, почему Redis вынесен в отдельный compose-файл, — в [docs/docker.md](docker.md#redis).

## 💻 Запуск без Docker

Если Redis поднят только через `docker run -p 6379:6379 redis:7-alpine` (или установлен на хосте) и слушает `localhost:6379`, значения по умолчанию в `.env` (`REDIS_HOST=localhost`) работают без изменений:

```powershell
docker run -d --name redis -p 6379:6379 redis:7-alpine
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/api/v1/redis-check
```

## 🔍 Диагностика

Если `/api/v1/redis-check` возвращает «не подключен к redis»:

1. Проверить, что контейнер `redis` вообще поднят и здоров: `docker compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml ps` (без `-f docker/docker-compose.redis.yml` контейнер не создаётся вовсе).
2. Проверить `REDIS_HOST`/`REDIS_PORT`/`REDIS_PASSWORD`/`REDIS_DB` в `.env`.
3. Если приложение запущено вне Docker, а Redis — внутри (или наоборот) — учесть, что `localhost` внутри контейнера указывает на сам контейнер, а не на хост-машину.

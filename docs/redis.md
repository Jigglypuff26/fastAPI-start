# Redis

Подключение к Redis, переменные окружения и проверка соединения.

## Переменные окружения

Параметры подключения задаются в [app/core/config.py](../app/core/config.py) отдельными полями `Settings`, читаемыми из `.env`:

| Переменная       | Описание                                             | Пример      |
| ---------------- | ----------------------------------------------------- | ----------- |
| `REDIS_HOST`     | Хост Redis                                            | `localhost` |
| `REDIS_PORT`     | Порт Redis                                            | `6379`      |
| `REDIS_PASSWORD` | Пароль (пусто — без аутентификации)                   | —           |
| `REDIS_DB`       | Номер логической базы Redis                           | `0`         |

Значения по умолчанию (для локальной разработки) заданы в [.env.example](../.env.example). Реальные значения — в `.env`, который не попадает в git (см. [docs/security.md](security.md#секреты-и-env)).

## Проверка подключения

Эндпоинт `GET /redis-check` пытается подключиться к Redis и выполнить `PING`:

- `{"message": "подключен к redis"}` — соединение установлено.
- `{"message": "не подключен к redis"}` — соединение не удалось (неверные креды, Redis недоступен и т.п.).

Реализация:

- [app/core/redis_client.py](../app/core/redis_client.py) — `check_redis_connection()`, подключается через [redis-py](https://github.com/redis/redis-py) (`redis.asyncio`) с таймаутом 3 секунды, любую ошибку подключения превращает в `False`.
- [app/routers/http/redis.py](../app/routers/http/redis.py) — сам роут.

## Запуск Redis через Docker

Redis поднимается как отдельный сервис `redis` в [docker/docker-compose.yml](../docker/docker-compose.yml) (образ `redis:7-alpine`, данные сохраняются в volume `redis-data`, порт `6379` проброшен на хост):

```powershell
docker compose -f docker/docker-compose.yml up --build
```

При таком запуске сервис `api` обращается к Redis по имени сервиса — `REDIS_HOST=redis` переопределяется в `environment` секции `api` в `docker-compose.yml` (аналогично тому, как `DB_HOST` переопределяется для Postgres, см. [docs/database.md](database.md)).

## Запуск без Docker

Если Redis поднят только через `docker run -p 6379:6379 redis:7-alpine` (или установлен на хосте) и слушает `localhost:6379`, значения по умолчанию в `.env` (`REDIS_HOST=localhost`) работают без изменений:

```powershell
docker run -d --name redis -p 6379:6379 redis:7-alpine
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/redis-check
```

## Диагностика

Если `/redis-check` возвращает «не подключен к redis»:

1. Проверить, что контейнер `redis` запущен и здоров: `docker compose -f docker/docker-compose.yml ps`.
2. Проверить `REDIS_HOST`/`REDIS_PORT`/`REDIS_PASSWORD`/`REDIS_DB` в `.env`.
3. Если приложение запущено вне Docker, а Redis — внутри (или наоборот) — учесть, что `localhost` внутри контейнера указывает на сам контейнер, а не на хост-машину.

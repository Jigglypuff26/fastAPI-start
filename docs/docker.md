# Docker

Настройка и запуск проекта в Docker — отдельно для prod и для разработки.

Все Docker-файлы лежат в [docker/](../docker/):

- [Dockerfile.prod](../docker/Dockerfile.prod) — prod-образ: код запечён в образ, запуск от непривилегированного пользователя (`appuser`), без reload.
- [Dockerfile.dev](../docker/Dockerfile.dev) — dev-образ: добавлены dev-зависимости (`requirements-dev.txt`) для тестов и линтинга, `uvicorn` запускается с `--reload`.
- [docker-compose.yml](../docker/docker-compose.yml) — prod-стек (healthcheck, `restart: unless-stopped`).
- [docker-compose.dev.yml](../docker/docker-compose.dev.yml) — dev-оверрайд поверх prod-стека: код монтируется volume'ом с хоста, `DEBUG=true`.

Все команды ниже выполняются из корня проекта — контекст сборки в compose-файлах указывает на корень (`context: ..`).

## Prod

Код запечён в образ на этапе сборки, контейнер работает от непривилегированного пользователя, reload отключён:

```powershell
docker compose -f docker/docker-compose.yml up --build
```

## Dev

Код монтируется volume'ом с хоста, `uvicorn --reload` подхватывает изменения на лету без пересборки образа:

```powershell
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build
```

Запуск тестов/линтера внутри dev-контейнера:

```powershell
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml run --rm api pytest
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml run --rm api python scripts/lint.py
```

## Без compose

Напрямую через Docker, без compose (только prod-образ):

```powershell
docker build -f docker/Dockerfile.prod -t fastapi-project .
docker run -p 8000:8000 --env-file .env fastapi-project
```

## Переменные окружения

Если файл `.env` отсутствует, приложение при старте само создаст его из `.env.example` (см. [app/core/env.py](../app/core/env.py)). В `docker-compose.yml`/`docker-compose.dev.yml` `.env` подключён как `env_file` и необязателен (`required: false`) — при его отсутствии применяются значения по умолчанию из кода/образа.

### Подключение к Postgres на хосте

`DB_HOST` в `.env` обычно указывает на `localhost` для запуска приложения напрямую (без Docker). Внутри контейнера `localhost` — это сам контейнер, а не хост-машина, поэтому `docker-compose.yml` переопределяет `DB_HOST=host.docker.internal` в секции `environment` (переопределяет значение из `env_file`). На Linux-хостах для работы `host.docker.internal` может дополнительно понадобиться `extra_hosts: ["host.docker.internal:host-gateway"]`.

Подробнее про переменные подключения и диагностику — в [docs/database.md](database.md).

## Остановка

```powershell
docker compose -f docker/docker-compose.yml down
```

Для dev-стека — та же команда с добавлением `-f docker/docker-compose.dev.yml`.

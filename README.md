# 🚀 FastAPI Boilerplate

## 📖 Описание проекта

Boilerplate-проект на [FastAPI](https://fastapi.tiangolo.com/) для быстрого старта разработки бэкенд-сервисов. Содержит готовую базовую структуру, поверх которой можно сразу начинать писать бизнес-логику: роутеры, конфигурация через переменные окружения, обработка ошибок, CORS, подключение к PostgreSQL и Redis, тесты и Docker.

Структура проекта:

```
fastApi/
├── app/
│   ├── __init__.py
│   ├── main.py            # создание приложения, CORS, обработка ошибок, подключение роутеров
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # настройки приложения (Pydantic Settings, .env)
│   │   ├── env.py               # ensure_env_file — создание .env из .env.example
│   │   ├── limiter.py           # rate limiting (slowapi)
│   │   ├── security_headers.py  # middleware с security-заголовками
│   │   ├── ip_allowlist.py      # middleware: ограничение доступа по IP (ALLOWED_IPS)
│   │   ├── db.py                # async engine, пул соединений, сессии SQLAlchemy к PostgreSQL
│   │   └── redis_client.py      # пул соединений Redis (ConnectionPool)
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py              # Base (DeclarativeBase) — сюда подключаются модели для Alembic
│   └── routers/
│       ├── __init__.py
│       ├── http/
│       │   ├── __init__.py
│       │   ├── root.py    # роутер с эндпоинтом /
│       │   ├── postgre.py # роутер с эндпоинтом /postgre-check
│       │   └── redis.py   # роутер с эндпоинтом /redis-check
│       └── ws/
│           ├── __init__.py
│           └── echo.py    # WebSocket-эхо на /ws
├── tests/
│   ├── __init__.py
│   ├── test_root.py       # тесты на GET /
│   ├── test_rate_limit.py # тесты на rate limiting (slowapi, 429 при превышении)
│   └── test_ws_echo.py    # тесты на WebSocket /ws
├── venv/                  # виртуальное окружение (в git не попадает)
├── requirements.txt       # зависимости для запуска
├── requirements-dev.txt   # зависимости для разработки (тесты, линтинг и т.д.)
├── scripts/
│   └── lint.py            # одной командой: Black + Flake8 + mypy
├── docs/
│   ├── security.md        # что настроено по безопасности и где в коде
│   ├── docker.md          # настройка и запуск проекта в Docker (prod/dev)
│   ├── database.md        # подключение к PostgreSQL и /postgre-check
│   └── redis.md           # подключение к Redis и /redis-check
├── migrations/             # Alembic: миграции схемы БД
│   ├── env.py              # конфигурация Alembic (URL и metadata берутся из app/)
│   └── versions/           # файлы миграций
├── alembic.ini             # конфигурация Alembic (script_location, логирование)
├── pyproject.toml         # настройки Black и mypy
├── .flake8                # настройки Flake8
├── .pre-commit-config.yaml # хуки: black, flake8, mypy и базовые проверки
├── .env.example           # пример файла с переменными окружения
├── docker/
│   ├── Dockerfile.prod          # prod-образ: non-root, без reload
│   ├── Dockerfile.dev           # dev-образ: reload, dev-зависимости
│   ├── docker-compose.yml          # prod-стек (без Postgres и Redis)
│   ├── docker-compose.dev.yml      # dev-оверрайд (volume, DEBUG=true)
│   ├── docker-compose.postgres.yml # опциональный оверрайд: поднимает сервис db (Postgres)
│   └── docker-compose.redis.yml    # опциональный оверрайд: поднимает сервис redis
├── .dockerignore
├── .gitignore
└── README.md
```

## 📦 Установка зависимостей

1. Создать виртуальное окружение (если ещё не создано):

   ```powershell
   python -m venv venv
   ```

2. Активировать виртуальное окружение:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Установить зависимости:

   ```powershell
   pip install -r requirements.txt
   ```

   Для разработки (с тестами):

   ```powershell
   pip install -r requirements-dev.txt
   ```

4. `.env` создаётся автоматически из `.env.example` при первом запуске приложения (см. `app/core/config.py` и `app/core/env.py`), если файла ещё нет. Существующий `.env` при этом не перезаписывается. При необходимости отредактируйте значения в `.env` после его создания.

## ▶️ Запуск проекта

```powershell
uvicorn app.main:app --reload
```

После запуска сервер будет доступен по адресу [http://127.0.0.1:8000](http://127.0.0.1:8000).

Документация API (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 🐳 Запуск через Docker

Настройка и запуск в Docker (prod и dev) — в [docs/docker.md](docs/docker.md).

## ⏹️ Остановка проекта

Если сервер запущен в текущем терминале — нажать `Ctrl+C`.

Если сервер запущен в фоне, остановить процесс, слушающий порт 8000:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

## 🧪 Тесты

```powershell
pytest
```

## 🧹 Форматирование и линтинг

Форматирование кода — [Black](https://black.readthedocs.io/), линтинг — [Flake8](https://flake8.pycqa.org/) (настройки в `pyproject.toml` и `.flake8`).

Запустить форматирование и все проверки (Black, Flake8, mypy) одной командой:

```powershell
python scripts/lint.py
```

Проверить форматирование без изменения файлов:

```powershell
black --check .
```

Отформатировать код:

```powershell
black .
```

Проверить линтинг:

```powershell
flake8
```

Проверить типизацию — [mypy](https://mypy-lang.org/) в строгом режиме (настройки в `pyproject.toml`):

```powershell
mypy app
```

### 🪝 Pre-commit hooks

Black, Flake8, mypy и базовые проверки (trailing whitespace, конфликты слияния и т.д.) запускаются автоматически перед каждым коммитом через [pre-commit](https://pre-commit.com/) (настройки в `.pre-commit-config.yaml`).

Установить хуки (один раз после клонирования репозитория):

```powershell
pre-commit install
```

Прогнать все хуки по всем файлам вручную:

```powershell
pre-commit run --all-files
```

## 🔒 Безопасность

Обзор настроенных мер базовой безопасности (CORS, security-заголовки, скрытие Swagger в продакшене, TrustedHost, IP allowlist, rate limiting) и того, где они находятся в коде — в [docs/security.md](docs/security.md).

## 🗄️ База данных

Переменные окружения для подключения к PostgreSQL, эндпоинт `/postgre-check` и диагностика — в [docs/database.md](docs/database.md).

## 🧬 Миграции БД (Alembic)

Схема БД версионируется через [Alembic](https://alembic.sqlalchemy.org/), URL подключения берётся из `.env` через `app.core.config.settings` (см. [migrations/env.py](migrations/env.py)).

Применить все миграции:

```powershell
alembic upgrade head
```

Создать новую миграцию (после добавления/изменения моделей в `app/models/`):

```powershell
alembic revision --autogenerate -m "описание изменения"
```

Откатить последнюю миграцию:

```powershell
alembic downgrade -1
```

## ⚡ Redis

Переменные окружения для подключения к Redis, запуск Redis через Docker, эндпоинт `/redis-check` и диагностика — в [docs/redis.md](docs/redis.md).

## Эндпоинты

### 👋 `GET /`

Возвращает приветственное сообщение.

**Ответ:**

```json
{
  "message": "hellow fastapi"
}
```

### 🗄️ `GET /postgre-check`

Проверяет подключение к PostgreSQL. Подробности — в [docs/database.md](docs/database.md).

**Ответ:**

```json
{
  "message": "подключен к базе"
}
```

### ⚡ `GET /redis-check`

Проверяет подключение к Redis. Подробности — в [docs/redis.md](docs/redis.md).

**Ответ:**

```json
{
  "message": "подключен к redis"
}
```

### 🔌 `WS /ws`

WebSocket-эхо: отправленное сообщение возвращается обратно тем же текстом. При `DEBUG=true` доступна тестовая HTML-страница на `GET /ws/test`.

## ➕ Как добавить новый эндпоинт

1. Создайте роутер в `app/routers/http/` (для HTTP) или `app/routers/ws/` (для WebSocket), например `app/routers/http/items.py`:

   ```python
   from fastapi import APIRouter

   router = APIRouter(prefix="/items", tags=["items"])


   @router.get("/")
   def list_items() -> list[str]:
       return []
   ```

2. Подключите роутер в `app/main.py`:

   ```python
   from app.routers.http import items

   app.include_router(items.router)
   ```

   Если у эндпоинта нужен rate limiting — навесьте `@limiter.limit(settings.rate_limit)` явно (см. [docs/security.md](docs/security.md) про особенности `SlowAPIMiddleware` в этом проекте).

3. Добавьте тесты в `tests/` (по аналогии с `tests/test_root.py`), например `tests/test_items.py`:

   ```python
   from fastapi.testclient import TestClient

   from app.main import app

   client = TestClient(app)


   def test_list_items() -> None:
       response = client.get("/items/")

       assert response.status_code == 200
       assert response.json() == []
   ```

4. Проверьте эндпоинт вручную через Swagger ([http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)) и запустите тесты:

   ```powershell
   pytest
   ```

5. Опишите новый эндпоинт в разделе [Эндпоинты](#эндпоинты) этого README.

## 💬 От автора

Этот проект разрабатывался исходя из личного опыта — как удобный стартовый набор для собственных задач. Дорабатывайте и меняйте как считаете нужным, и если не трудно — поставьте ⭐ репозиторию, если он оказался полезен.

# 📝 Логирование

Обзор того, как в приложении настроено логирование, и где это находится в коде.

## Формат

Логи пишутся в stdout одной JSON-строкой на запись — так их проще собирать и парсить агрегаторами логов (ELK, Loki, CloudWatch и т.п.), чем произвольный текстовый вывод. Пример строки:

```json
{"timestamp": "2026-07-16T12:00:00+0000", "level": "INFO", "logger": "app.request", "message": "GET / 200 3.42ms", "request_id": "b6b6a9b0-...", "method": "GET", "path": "/", "status_code": 200, "duration_ms": 3.42, "client_ip": "127.0.0.1"}
```

Настроено в [app/core/logging.py](../app/core/logging.py), уровень логирования задаётся `LOG_LEVEL` в `.env` (по умолчанию `INFO`). Вызывается один раз при импорте [app/main.py](../app/main.py), до создания FastAPI-приложения.

## `request_id`

На каждый запрос генерируется `request_id` (или берётся из входящего заголовка `X-Request-ID`, если запрос уже прошёл через другой сервис/gateway) — так по одному значению можно найти все логи одного запроса, в том числе в разных сервисах, если они пробрасывают этот заголовок дальше.

- Возвращается клиенту в заголовке ответа `X-Request-ID`.
- Автоматически подставляется в каждую запись лога через `RequestIdFilter`, независимо от того, где в коде вызван `logging.getLogger(...)` — не нужно явно прокидывать `request_id` в сервисный слой.
- Доступен в обработчиках как `request.state.request_id` (см. [app/core/error_handlers.py](../app/core/error_handlers.py)) — попадает в JSON-тело ответа об ошибке, см. [docs/errors.md](errors.md).

Реализовано в [app/core/request_logging.py](../app/core/request_logging.py) (`RequestIdMiddleware`), подключено как middleware в [app/main.py](../app/main.py) последним по регистрации — оборачивает все остальные middleware, поэтому request_id и лог о завершении запроса есть даже у запросов, отклонённых `IPAllowlistMiddleware`/`TrustedHostMiddleware`.

## Лог завершения запроса

На каждый запрос пишется одна запись уровня `INFO` в логгер `app.request`: метод, путь, код ответа, длительность в мс, IP клиента. Этого достаточно, чтобы увидеть отклонённые запросы (403 от IP allowlist, 429 от rate limiting, 400 от TrustedHost) без необходимости логировать отказ в каждом middleware отдельно.

## Логирование из сервисного кода

Любой модуль может логировать через стандартный `logging`:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Заказ создан", extra={"order_id": order.id})
```

Поля из `extra` попадают в итоговый JSON как есть (см. `JsonFormatter` в [app/core/logging.py](../app/core/logging.py)) — не нужно расширять форматтер под каждое новое поле.

## Необработанные исключения

Полный traceback необработанного исключения пишется в лог (`logger.exception`, логгер `app.errors`) при обработке в [app/core/error_handlers.py](../app/core/error_handlers.py) — клиенту при этом уходит только общее сообщение и `request_id`, см. [docs/errors.md](errors.md).

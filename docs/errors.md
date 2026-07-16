# ⚠️ Обработка ошибок

Обзор единого формата ответа об ошибке и того, где это находится в коде.

## Формат ответа

Любая ошибка — HTTP-исключение, ошибка валидации запроса или необработанное исключение — возвращается клиенту в одном и том же формате:

```json
{
  "error": {
    "type": "http_error",
    "message": "Not Found"
  },
  "request_id": "b6b6a9b0-1234-4c8a-9a1b-000000000000"
}
```

`error.type` — один из:

- `http_error` — намеренно вызванный `HTTPException` (404, 403, 401 и т.п.).
- `validation_error` — тело/параметры запроса не прошли валидацию Pydantic (422). Дополнительно содержит `error.details` — список ошибок в формате `RequestValidationError.errors()`.
- `internal_error` — необработанное исключение (500). Клиенту уходит только общее сообщение `"Internal server error"`, без деталей исключения — полный traceback пишется в лог, см. [docs/logging.md](logging.md).

`request_id` — id запроса, по которому можно найти связанные записи в логах (см. [docs/logging.md](logging.md)).

## Реализация

Три обработчика в [app/core/error_handlers.py](../app/core/error_handlers.py), подключены в [app/main.py](../app/main.py):

- `http_exception_handler` — заменяет дефолтный обработчик FastAPI для `HTTPException`.
- `validation_exception_handler` — заменяет дефолтный обработчик FastAPI для `RequestValidationError`.
- `unhandled_exception_handler` — ловит всё остальное, логирует traceback и возвращает 500.

**Rate limiting** (`slowapi`, 429 при превышении `RATE_LIMIT`) обрабатывается отдельно, стандартным обработчиком `slowapi` (см. [docs/security.md](security.md)), и пока не приведён к этому же формату — при необходимости можно обернуть.

## Как использовать в своих роутерах

Ничего дополнительно подключать не нужно — достаточно поднять `HTTPException` или дать Pydantic провалить валидацию, формат ответа применится автоматически:

```python
from fastapi import HTTPException


@router.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    item = find_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

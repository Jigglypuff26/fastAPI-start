import json
import logging
import sys
from contextvars import ContextVar
from typing import Any

# Текущий request_id доступен из любого места, без необходимости прокидывать
# request через все вызовы — middleware проставляет значение на вход запроса,
# RequestIdFilter подставляет его в каждую запись лога.
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")

_RESERVED_LOG_RECORD_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
    "request_id",
}


class RequestIdFilter(logging.Filter):
    """Добавляет request_id текущего запроса в каждую запись лога."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get()
        return True


class JsonFormatter(logging.Formatter):
    """Форматирует записи лога в одну JSON-строку на строку вывода — так
    логи проще собирать и парсить агрегаторами (ELK, Loki и т.п.), чем
    произвольный текстовый формат.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        # Всё, что передано через logger.info(..., extra={...}), попадает в
        # итоговый JSON как есть — не нужно расширять форматтер под каждое
        # новое поле, которое понадобится сервисному коду.
        for key, value in record.__dict__.items():
            if key not in _RESERVED_LOG_RECORD_ATTRS and key not in payload:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str) -> None:
    """Настраивает root-логгер: один JSON-хендлер в stdout, уровень из настроек.

    Вызывается один раз при старте приложения (см. app/main.py), до создания
    FastAPI-приложения, чтобы логи lifespan и самого старта тоже шли в нужном
    формате.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())

import logging

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")


def _envelope(
    error_type: str, message: str, request: Request, details: object = None
) -> dict[str, object]:
    error: dict[str, object] = {"type": error_type, "message": message}
    if details is not None:
        error["details"] = details
    return {
        "error": error,
        "request_id": getattr(request.state, "request_id", "-"),
    }


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope("http_error", str(exc.detail), request),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_envelope(
            "validation_error",
            "Validation error",
            request,
            details=jsonable_encoder(exc.errors()),
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Полный traceback — в лог (для диагностики), клиенту — только общее
    # сообщение и request_id, по которому можно найти этот лог.
    logger.exception("Unhandled exception while processing request", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=_envelope("internal_error", "Internal server error", request),
    )

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.limiter import limiter

router = APIRouter(prefix="/api/v1", tags=["healthcheck"])
_PATH = "/healthcheck"
# Полный путь (с префиксом роутера) — для тестов, которым нужен реальный
# адрес эндпоинта, а не относительный внутри роутера.
ROOT_PATH = f"{router.prefix}{_PATH}"


@router.get(_PATH)
@limiter.limit(settings.rate_limit)
def healthcheck(request: Request) -> dict[str, str]:
    return {"status": "ok"}

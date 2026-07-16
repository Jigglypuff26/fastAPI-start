from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.db import check_postgres_connection
from app.core.limiter import limiter

router = APIRouter(prefix="/api/v1", tags=["database"])
ROOT_PATH = "/postgre-check"


@router.get(ROOT_PATH)
@limiter.limit(settings.rate_limit)
async def postgre_check(request: Request) -> dict[str, str]:
    if not settings.db_enabled:
        return {"message": "проверка отключена (DB_ENABLED=false)"}
    if await check_postgres_connection():
        return {"message": "подключен к базе"}
    return {"message": "не подключен к базе"}

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.limiter import limiter
from app.core.redis_client import check_redis_connection

router = APIRouter()
ROOT_PATH = "/redis-check"


@router.get(ROOT_PATH)
@limiter.limit(settings.rate_limit)
async def redis_check(request: Request) -> dict[str, str]:
    if await check_redis_connection():
        return {"message": "подключен к redis"}
    return {"message": "не подключен к redis"}

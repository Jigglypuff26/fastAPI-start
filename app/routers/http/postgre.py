from fastapi import APIRouter

from app.core.config import settings
from app.core.db import check_postgres_connection

router = APIRouter()
ROOT_PATH = "/postgre-check"


@router.get(ROOT_PATH)
async def postgre_check() -> dict[str, str]:
    if not settings.db_enabled:
        return {"message": "проверка отключена (DB_ENABLED=false)"}
    if await check_postgres_connection():
        return {"message": "подключен к базе"}
    return {"message": "не подключен к базе"}

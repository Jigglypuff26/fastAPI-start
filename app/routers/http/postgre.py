from fastapi import APIRouter

from app.core.db import check_postgres_connection

router = APIRouter()
ROOT_PATH = "/postgre-check"


@router.get(ROOT_PATH)
async def postgre_check() -> dict[str, str]:
    if await check_postgres_connection():
        return {"message": "подключен к базе"}
    return {"message": "не подключен к базе"}

import asyncpg

from app.core.config import settings


async def check_postgres_connection() -> bool:
    try:
        conn = await asyncpg.connect(settings.database_url, timeout=3)
    except Exception:
        return False

    try:
        await conn.execute("SELECT 1")
    finally:
        await conn.close()
    return True

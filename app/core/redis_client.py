from redis.asyncio import Redis

from app.core.config import settings


async def check_redis_connection() -> bool:
    client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password or None,
        db=settings.redis_db,
        socket_connect_timeout=3,
        socket_timeout=3,
    )
    try:
        return bool(await client.ping())
    except Exception:
        return False
    finally:
        await client.aclose()

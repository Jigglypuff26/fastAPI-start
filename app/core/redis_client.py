from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

redis_pool = ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password or None,
    db=settings.redis_db,
    socket_connect_timeout=3,
    socket_timeout=3,
    max_connections=settings.redis_max_connections,
)


def get_redis() -> Redis:
    """FastAPI-dependency: возвращает клиент Redis на основе общего пула соединений."""
    return Redis(connection_pool=redis_pool)


async def check_redis_connection() -> bool:
    client = get_redis()
    try:
        return bool(await client.ping())
    except Exception:
        return False

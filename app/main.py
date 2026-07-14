from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.db import engine
from app.core.ip_allowlist import IPAllowlistMiddleware
from app.core.limiter import limiter
from app.core.redis_client import redis_pool
from app.core.security_headers import SecurityHeadersMiddleware
from app.routers.http import postgre, redis, root
from app.routers.ws import echo


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()
    await redis_pool.disconnect()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, _rate_limit_exceeded_handler  # type: ignore[arg-type]
)

# Middleware применяются в порядке, обратном регистрации, поэтому
# IPAllowlistMiddleware и TrustedHostMiddleware (добавлены последними) отклоняют
# некорректные запросы раньше, чем выполнится любая другая работа.
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(IPAllowlistMiddleware, allowed_ips=settings.allowed_ips)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(root.router)
app.include_router(postgre.router)
app.include_router(redis.router)
app.include_router(echo.router)

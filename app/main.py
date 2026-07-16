from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.db import engine
from app.core.error_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.ip_allowlist import IPAllowlistMiddleware
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.core.redis_client import redis_pool
from app.core.request_logging import RequestIdMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.routers.http import healthcheck, postgre, redis
from app.routers.ws import echo

configure_logging(settings.log_level)


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

# Middleware применяются в порядке, обратном регистрации — каждый следующий
# add_middleware оборачивает предыдущие снаружи и выполняется раньше них.
# Поэтому TrustedHostMiddleware и IPAllowlistMiddleware (добавлены позже
# SecurityHeaders/CORS) отклоняют некорректные запросы раньше, чем выполнится
# остальная работа, а RequestIdMiddleware (добавлен последним из всех) —
# самый внешний и выполняется первым: request_id и лог доступа есть даже у
# запросов, отклонённых IPAllowlistMiddleware/TrustedHostMiddleware.
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
app.add_middleware(RequestIdMiddleware)

app.add_exception_handler(
    StarletteHTTPException, http_exception_handler  # type: ignore[arg-type]
)
app.add_exception_handler(
    RequestValidationError, validation_exception_handler  # type: ignore[arg-type]
)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Все роутеры версионируются через APIRouter(prefix="/api/v1", tags=[...])
# в самом роутере, включая healthcheck — см. app/routers/http/healthcheck.py.
app.include_router(healthcheck.router)
app.include_router(postgre.router)
app.include_router(redis.router)
app.include_router(echo.router)

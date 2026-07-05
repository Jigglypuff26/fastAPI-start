from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.limiter import limiter

router = APIRouter()

ROOT_PATH = "/"


@router.get(ROOT_PATH)
@limiter.limit(settings.rate_limit)
def read_root(request: Request) -> dict[str, str]:
    return {"message": "hellow fastapi"}

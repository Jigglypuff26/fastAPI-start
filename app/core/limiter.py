from slowapi import Limiter
from slowapi.util import get_remote_address

# default_limits здесь не задаются: из-за ленивого подключения роутеров в этой
# версии FastAPI app.routes нельзя штатно обойти для автоопределения эндпоинтов,
# поэтому автоматическое применение через SlowAPIMiddleware не срабатывает.
# Каждый роут должен явно подключать лимит через @limiter.limit(...).
limiter = Limiter(key_func=get_remote_address)

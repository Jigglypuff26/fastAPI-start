from slowapi import Limiter
from slowapi.util import get_remote_address

# No default_limits here: this FastAPI version's lazy router inclusion means
# app.routes can't be walked to auto-detect endpoints, so SlowAPIMiddleware's
# automatic enforcement is a no-op. Routes must opt in with @limiter.limit(...).
limiter = Limiter(key_func=get_remote_address)

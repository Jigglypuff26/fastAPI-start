import ipaddress
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class IPAllowlistMiddleware(BaseHTTPMiddleware):
    """Rejects requests from client IPs not in the allowlist.

    An empty allowlist disables the check (allows everyone), which is the
    default so the app keeps working unconfigured.
    """

    def __init__(self, app: ASGIApp, allowed_ips: list[str]) -> None:
        super().__init__(app)
        self._networks = [ipaddress.ip_network(ip, strict=False) for ip in allowed_ips]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if self._networks and not self._is_allowed(request):
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})
        return await call_next(request)

    def _is_allowed(self, request: Request) -> bool:
        if request.client is None:
            return False
        try:
            client_ip = ipaddress.ip_address(request.client.host)
        except ValueError:
            return False
        return any(client_ip in network for network in self._networks)

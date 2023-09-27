# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation, unused-import
from fastapi import Request
from starlette.datastructures import URL
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

class SSROAuth2Middleware(BaseHTTPMiddleware):
    def __init__(self, app, config, callback=None):
        super().__init__(app)
        self.oauth2_middleware = OAuth2Middleware(app, config, callback)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # logger.debug(f"route.path: {URL(scope=scope).path}")
        if any(route.path == URL(scope=scope).path for route in router_api.routes):
            await super().__call__(scope, receive, send)
        else:
            return await self.oauth2_middleware.__call__(scope, receive, send)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        return await call_next(request)


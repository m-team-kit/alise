# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation, unused-import

from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi import Request
from starlette.datastructures import URL
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from alise.router_api import router_api


class SSROAuth2Middleware(BaseHTTPMiddleware):
    def __init__(self, app, config, callback=None):
        super().__init__(app)
        if callback is not None:
            self.oauth2_middleware = OAuth2Middleware(app, config, callback)
        else:
            self.oauth2_middleware = OAuth2Middleware(app, config)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Make sure /api is never passed to super()"""
        URL_path = URL(scope=scope).path.split("/")[1:2]
        URL_start = "/" + "/".join(URL_path)
        if URL_start == "/api":
            await super().__call__(scope, receive, send)
        else:
            # print("xxxxxxx: upstream")
            return await self.oauth2_middleware.__call__(scope, receive, send)

    # async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
    #     for route in router_api.routes:
    #         print(F"route: {route}")
    #     print(F"route.path: {route.path}")
    #     print(F"URL(scope=scope): {URL(scope=scope).path}")
    #     if any(
    #         route.path == URL(scope=scope).path  # pyright: ignore
    #         for route in router_api.routes
    #     ):
    #         print("xxxxxxx: mine")
    #         await super().__call__(scope, receive, send)
    #     else:
    #         print("xxxxxxx: upstream")
    #         return await self.oauth2_middleware.__call__(scope, receive, send)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        return await call_next(request)

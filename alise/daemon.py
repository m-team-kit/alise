"""Daemon for alise."""
# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation, unused-import

import uvicorn
import sys

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi_oauth2.middleware import Auth
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router

from alise.logsetup import logger
from alise.config import CONFIG
from alise.parse_args import args

from alise.oauth2_config import oauth2_config
from alise.router_api import router_api
from alise.router_ssr import router_ssr
# from alise.marcus_oauth2 import router as marcus_oauth2_router


app = FastAPI()
app2 = FastAPI()

app.include_router(router_ssr)
app2.include_router(router_api)

# app.include_router(marcus_oauth2_router) # overwrite oauth2/{provider}/token endpoint
app.include_router(oauth2_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/api", app2)

# app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)
app.add_middleware(OAuth2Middleware, config=oauth2_config)

logger.debug("===============================================================")


def main():
    """Console script for alise."""
    logger.debug("This is just a test for 'debug'")
    logger.info("This is just a test for 'info'")
    logger.warning("This is just a test for 'warning'")
    logger.error("This is just a test for 'error'")

    # uvicorn.run(root, host="0.0.0.0", port=4711)
    # uvicorn.run(root, host="0.0.0.0", port=8000, log_level="info")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    logger.debug("--------startup done----------")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

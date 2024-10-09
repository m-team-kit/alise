"""Daemon for alise."""

# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation

import sys
import os
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi_oauth2.router import router as oauth2_router

from alise.logsetup import logger

# from alise.config import CONFIG
# from alise.parse_args import args

from alise.pathdiversion import SSROAuth2Middleware

from alise.oauth2_config import oauth2_config
from alise.router_api import router_api
from alise.router_ssr import router_ssr

# from alise.marcus_oauth2 import router as marcus_oauth2_router


app = FastAPI()

app.include_router(router_ssr)
app.include_router(router_api)
app.include_router(oauth2_router)

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# for r in router_api.routes:
#     logger.debug(f"router_api.routes: {r}")
# logger.debug(f"router_api.routes: {type(router_api.routes)}")
# for r in router_ssr.routes:
#     logger.debug(f"router_ssr.routes: {r}")
# logger.debug(f"router_ssr.routes: {type(router_ssr.routes)}")

# app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)
# app.add_middleware(OAuth2Middleware, config=oauth2_config)


# app.add_middleware(SSROAuth2Middleware, config=oauth2_config, callback=on_auth)
app.add_middleware(SSROAuth2Middleware, config=oauth2_config)


def main():
    """Console script for alise."""
    # logger.debug("This is just a test for 'debug'")
    # logger.info("This is just a test for 'info'")
    # logger.warning("This is just a test for 'warning'")
    # logger.error("This is just a test for 'error'")

    # uvicorn.run(root, host="0.0.0.0", port=4711)
    # uvicorn.run(root, host="0.0.0.0", port=8000, log_level="info")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    logger.debug("--------startup done----------")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

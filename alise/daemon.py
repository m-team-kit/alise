"""Daemon for alise."""
# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation, unused-import

import uvicorn

from alise.logsetup import logger
from alise.config import CONFIG
from alise.parse_args import args

from alise.oauth2_config import oauth2_config

from fastapi import FastAPI, Request, Response, status
# from fastapi import Depends, FastAPI, Request, Response
from fastapi.security import HTTPBasicCredentials, HTTPBearer

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from fastapi_oauth2.middleware import Auth
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.middleware import User
from fastapi_oauth2.router import router as oauth2_router
# from models import User as UserModel
# from alise.database import get_db
from alise.router_api import router_api
from alise.router_ssr import router_ssr
from alise.marcus_oauth2 import router as marcus_oauth2_router


async def on_auth(auth: Auth, user: User):
    # perform a check for user existence in
    # the database and create if not exists
    logger.debug("IMPLEMENT MEEEEEEEEEEEEE")
    # for attr in dir(user):
    #     logger.info(F"user: {attr:30} - {getattr(user, attr, '')}")
    # redirect_uri = request.cookies.get("redirect_uri", "nothin")
    # logger.debug(f"should redirect to {redirect_uri}")
    # db: Session = next(get_db())
    # query = db.query(UserModel)
    # if user.identity and not query.filter_by(identity=user.identity).first():
    #     # create a local user by OAuth2 user's data if it does not exist yet
    #     UserModel(**{
    #         "identity": user.identity,  # User property
    #         "username": user.get("username"),  # custom attribute
    #         "name": user.display_name,  # User property
    #         "image": user.picture,  # User property
    #         "email": user.email,  # User property
    #     }).save(db)

app = FastAPI()

app.include_router(router_ssr)

# app.include_router(marcus_oauth2_router) # overwrite oauth2/{provider}/token endpoint
app.include_router(oauth2_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)

logger.debug('===============================================================')



def main():
    """Console script for alise."""
    logger.debug("This is just a test for 'debug'")
    logger.info("This is just a test for 'info'")
    logger.warning("This is just a test for 'warning'")
    logger.error("This is just a test for 'error'")


    # uvicorn.run(root, host="0.0.0.0", port=4711)
    uvicorn.run(root, host="0.0.0.0", port=8000, log_level="info")



if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

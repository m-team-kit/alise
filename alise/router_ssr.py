# vim: tw=100 foldmethod=indent
# pylint: disable=logging-fstring-interpolation
import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates


from alise.oauth2_config import get_internal_providers
from alise.oauth2_config import get_external_providers

from alise.models import DatabaseUser

# from alise.models import LastPage

from alise.logsetup import logger

# logger = logging.getLogger(__name__)

router_ssr = APIRouter()
templates = Jinja2Templates(directory="templates")

@router_ssr.get("/{site}", response_class=HTMLResponse)
async def site(request: Request, site: str):
    logger.info(f"-----------------[{site}]-------------------------------------------------")
    cookies = []

    # favicon
    if site == "favicon.ico":
        logger.debug("Returning favicon.ico")
        return FileResponse("static/favicon.ico")

    # logging
    logger.info("[Cookies]")
    for i in ["login-status", "session-id", "marcus"]:
        logger.info(f"    {i:13}- {request.cookies.get(i, '')}")
    logger.info(f"[Authenticated]: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            provider_type = request.auth.provider.backend.provider_type
        except AttributeError:
            provider_type = "external"
        logger.info(f"    identity: {request.user.identity}")
        logger.info(
            f"    provider: {request.auth.provider.provider},"
            f"  {provider_type}"
        )

    # redirect user straight to login at provider, if not authenticated
    if not request.user.is_authenticated:
        redirect_auth = f"/oauth2/{site}/authorize"
        logger.debug(f"Redirecting back to {redirect_auth}")
        response = RedirectResponse(redirect_auth)
        # and also set the cookie so user gets sent to right page, when coming back

        # Redirect URI
        if request.url.__str__()[-11:] != "favicon.ico":
            logger.info(f"storing redirect_uri: {request.url.__str__()}")
            response.set_cookie(key="redirect_uri", value=request.url.__str__(), max_age=60)
        else:
            loger.info("ffffffffffffffffffaaaaaaaaaaaaaaaaavvvvvvvvvvvviiiiiiiiiiiiiiiccccccccccoooooooooooonnnnnnnnnnn")

        return response

    ####### authenticated user from here on ########################################################
    user = DatabaseUser(site)

    # session_id
    session_id = request.cookies.get("session-id", "")
    # FIXME: Make sure we can get that session id from any user id
    db_session_id = user.get_session_id_by_user_id(request.user.identity, provider_type)
    if db_session_id != session_id:
        logger.warning("SESSION ID MISMATCH:")
        logger.warning(F"    cookie: {session_id}")
        logger.warning(F"        db: {db_session_id}")
    if not session_id:
        # if request.user.is_authenticated:
        session_id = request.user.identity
        logger.info(f"setting session id: {session_id}")
    cookies.append({"key": "session-id", "value": session_id})

    # Store user information in user object and database
    if provider_type == "internal":
        request.user.is_authenticated_as_internal = True
        # for attr in dir(request.user):
        #     logger.info(F"request.user: {attr:30} - {getattr(request.user, attr, '')}")

        user.store_internal_user(request.user, session_id)
        cookies.append(
            {
                "key": "login-status",
                "value": f"login {request.auth.provider.provider} as {request.user.identity}",
            }
        )
    else:  # user is authenticated, but not an internal one
        request.user.identity = "this is a test"
        user.store_external_user(request.user, session_id)
        request.user.linkage_available = True

        # Linkage done

    user.load_all_identities(session_id)
    # logger.debug(F"user: {user.get_int_id()}")
    # logger.debug(F"user: {user.int_id}")
    # logger.debug(F"user: {user.ext_ids}")
    logger.debug(F"user: {user.int_id.identity}")

    for e in user.ext_ids:
        logger.debug(F"user: {e.identity}")
        logger.debug(F"    : {e.jsondata.identity}")

    response = templates.TemplateResponse(
        "site.html",
        {
            "json": json,
            "request": request,
            "external_providers": get_external_providers(),
            "user": user,
        },
    )
    for cookie in cookies:
        response.set_cookie(key=cookie["key"], value=cookie["value"], max_age=2592000)

    return response


@router_ssr.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.info(f"request cookie: {request.cookies.get('marcus', '')}")

    # session_id = request.cookies.get("session-id", "")
    # lp = LastPage()
    # url = lp.get(session_id)
    # logger.info(f"redirect url: {url}")

    redirect_uri = request.cookies.get("redirect_uri", "")
    if request.user.is_authenticated:
        if redirect_uri:
            logger.debug(f"Redirecting back to {redirect_uri}")
            return RedirectResponse(redirect_uri)

    response = templates.TemplateResponse(
        "root.html",
        {
            "json": json,
            "request": request,
            "internal_providers": get_internal_providers(),
        },
    )
    return response


# from fastapi_oauth2.security import OAuth2
# oauth2 = OAuth2()
# from database import get_db
# @router_ssr.get("/users", response_class=HTMLResponse)
# async def users(request: Request, db: Session = Depends(get_db), _: str = Depends(oauth2)):
#     return templates.TemplateResponse("users.html", {
#         "json": json,
#         "request": request,
#         "users": [
#             dict([(k, v) for k, v in user.__dict__.items() if not k.startswith("_")]) for user in db.query(User).all()
#         ],
#     })

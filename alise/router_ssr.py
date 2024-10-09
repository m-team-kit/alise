# vim: tw=100 foldmethod=indent
# pylint: disable=logging-fstring-interpolation
import json
import os

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from addict import Dict

from alise.oauth2_config import get_internal_providers
from alise.oauth2_config import get_external_providers
from alise.exceptions import InternalException

from alise.models import DatabaseUser

# from alise.models import LastPage

from alise.logsetup import logger

# logger = logging.getLogger(__name__)

router_ssr = APIRouter()
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)
static_path = os.path.join(os.path.dirname(__file__), "static")

# There are a few different conceptions I'm using in this code:
# request.user.is_authenticated is merely an information on whether the request.user object contains
# information. Interesting for the ALISE use-case is whether or not we can find a (much longer
# living) session_id in the cookies


def get_provider_type(request):
    try:
        return request.auth.provider.backend.provider_type
    except AttributeError:
        return "external"


def session_logger(request):
    logger.info(f"----------[{request.url}]------------------------------------------")
    # for attr in dir(request):
    #     logger.info(F"request: {attr:30} - {getattr(request, attr, '')}")
    logger.info("[Cookies]")
    for i in ["Authorization", "session_id", "redirect_uri"]:
        # for i in ["session_id", "redirect_uri"]:
        logger.info(f"    {i:13}- {request.cookies.get(i, '')}")
    logger.info(f"[Authenticated]: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        provider_type = get_provider_type(request)
        logger.info(f"    identity: {request.user.identity}")
        logger.info(f"    provider: {request.auth.provider.provider}," f"  {provider_type}")


@router_ssr.get("/privacy.html", response_class=HTMLResponse)
async def privacy():
    with open(rf"{static_path}/privacy.html", "r") as f:
        content = f.read()
    f.close()
    return HTMLResponse(content=content, status_code=202)


@router_ssr.get("/{site}", response_class=HTMLResponse)
async def site(request: Request, site: str):
    # get cookie info
    session_id = request.cookies.get("session_id", "")
    cookies = []

    # favicon
    if site == "favicon.ico":
        logger.debug("Returning favicon.ico")
        return FileResponse("static/favicon.ico")

    # logging
    session_logger(request)
    # redirect user straight to login at provider, if not authenticated
    # if not session_id:
    if not request.user.is_authenticated:
        redirect_auth = f"/oauth2/{site}/authorize"
        logger.debug(f"Redirecting to authorize: {redirect_auth}")
        response = RedirectResponse(redirect_auth)
        # and also set the cookie so user gets sent to right page, when coming back

        # Redirect URI
        logger.info(f"storing redirect_uri: {str(request.url)}")
        response.set_cookie(key="redirect_uri", value=str(request.url), max_age=60)
        return response

    ####### authenticated user from here on ########################################################
    user = DatabaseUser(site)

    try:
        iss = request.auth.provider.backend.OIDC_ENDPOINT
        logger.info(f"found iss in backend config: {iss}")
    except AttributeError:
        raise InternalException(
            message=f"iss claim not found for {request.auth.provider.backend.name}"
        )
    logger.info(f"iss: {iss}")

    # FIXME: Make sure we can get that session id from any user id
    provider_type = get_provider_type(request)

    # Linkage
    db_session_id = user.get_session_id_by_user_id(request.user.identity, provider_type)
    if db_session_id != session_id:
        logger.warning("SESSION ID MISMATCH:")
        logger.warning(f"    cookie: {session_id}")
        logger.warning(f"        db: {db_session_id}")
    if not session_id:
        # if request.user.is_authenticated:
        session_id = request.user.identity
        logger.info(f"setting session id: {session_id}")
    cookies.append({"key": "session_id", "value": session_id})

    # Store user information in user object and database
    if provider_type == "internal":
        request.user.is_authenticated_as_internal = True

        user.store_internal_user(request.user, session_id)
    else:  # user is authenticated, but not an internal one
        # request.user.identity = "this is a test"
        user.store_external_user(request.user, session_id)

    logger.warning(f"CHECK SESSION ID!: {session_id}")
    # Linkage done

    # Act on linkage
    user.load_all_identities(session_id)
    # logger.debug(f"user (int_id): {user.int_id.identity}")

    # store linkage information with external_providers dict
    external_providers = []

    for ep in get_external_providers():
        external_providers.append(Dict())
        external_providers[-1].name = ep
        external_providers[-1].is_linked = False
        for ext_id in user.ext_ids:
            # logger.debug(f"user (ext_id): {ext_id.identity}")
            if ext_id.jsondata.provider == ep:
                external_providers[-1].is_linked = True
                # logger.info(f"im linked to this provider {ext_id.jsondata.provider}")

    response = templates.TemplateResponse(
        "site.html",
        {
            "json": json,
            "request": request,
            "external_providers": external_providers,
            "user": user,
            "current_site": site,
        },
    )
    for cookie in cookies:
        response.set_cookie(key=cookie["key"], value=cookie["value"], max_age=2592000)

    # # delete redirect_uri
    # response.delete_cookie(key="redirect_uri")

    return response


@router_ssr.get("/{site}/unlink/{provider}", response_class=HTMLResponse)
async def unlink(request: Request, site: str, provider: str):
    session_logger(request)

    # should_redirect_to = "/".join(request.url.__str__().split("/")[0:4])
    should_redirect_to = "/".join(str(request.url).split("/")[0:4])

    response = RedirectResponse("/oauth2/logout")
    response.set_cookie(key="redirect_uri", value=should_redirect_to)

    user = DatabaseUser(site)
    session_id = request.cookies.get("session_id", "")
    if not session_id:
        logger.error("cannot find user identity in this session!!!!!!!!!!!!!!!!!!")

    identity = user.get_identity_by_session_id(session_id, provider)
    logger.info(f"going to delete: identity: {identity} provider: {provider}")
    user.delete_external_user(identity, provider)
    return response


@router_ssr.get("/{site}/link/{provider}", response_class=HTMLResponse)
async def link(request: Request, site: str, provider: str):
    session_logger(request)

    # should_redirect_to = "/".join(request.url.__str__().split("/")[0:4])
    should_redirect_to = "/".join(str(request.url).split("/")[0:4])
    response = RedirectResponse(f"/oauth2/{provider}/authorize")
    response.set_cookie(key="redirect_uri", value=should_redirect_to)
    return response


@router_ssr.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session_logger(request)
    # session_id = request.cookies.get("session_id", "")
    # lp = LastPage()
    # url = lp.get(session_id)
    url = request.url
    logger.debug(f"redirect url: {url}")

    redirect_uri = request.cookies.get("redirect_uri", "")
    if redirect_uri:
        logger.info("redirecting to {redirect_uri}")
        response = RedirectResponse(redirect_uri)
        response.delete_cookie(key="redirect_uri")
        return response

    logger.debug(f"session_id: {request.user.identity}")
    if request.user.is_authenticated:
        if redirect_uri:
            logger.debug(f"Redirecting back to {redirect_uri}")
            response = RedirectResponse(redirect_uri)
            response.set_cookie(key="session_id", value=request.user.identity)
            logger.info("deleteing redirect uri cookie")
            response.delete_cookie(key="redirect_uri")
            # response.delete_cookie(key="Authorization")
            return response

    response = templates.TemplateResponse(
        "root.html",
        {
            "json": json,
            "request": request,
            "internal_providers": get_internal_providers(),
        },
    )
    return response

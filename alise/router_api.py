# vim: tw=100 foldmethod=indent
# pylint: disable=logging-fstring-interpolation

# from fastapi import FastAPI
from urllib.parse import unquote_plus

from addict import Dict
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse

from flaat.fastapi import Flaat
from alise.logsetup import logger
from alise import exceptions
from alise.oauth2_config import get_provider_name_by_iss
from alise.oauth2_config import get_sub_iss_by_identity
from alise.oauth2_config import get_provider_name_sub_by_identity

from alise.models import DatabaseUser

# app = FastAPI()
flaat = Flaat()
router_api = APIRouter(prefix="/api/v1")

flaat.set_trusted_OP_list(
    [
        "https://aai.egi.eu/auth/realms/egi",
        "https://accounts.google.com/",
        "https://login.helmholtz.de/oauth2/",
    ]
)

# session_id   - https%3A%2F%2Fsso.sling.si%3A8443%2Fauth%2Frealms%2FSLING@3c498039-1754-4f9d-b71c-5c13739e8875
# Identity:      https%3A%2F%2Fsso.sling.si%3A8443%2Fauth%2Frealms%2FSLING@3c498039-1754-4f9d-b71c-5c13739e8875


def fill_json_response(user):
    response_json = Dict()
    int_sub, int_iss = get_sub_iss_by_identity(user.int_id.identity)
    response_json.internal.sub = int_sub
    response_json.internal.iss = int_iss
    response_json.internal.username = user.int_id.jsondata.generated_username
    response_json.internal.display_name = user.int_id.jsondata.display_name

    response_json.external = []
    for e in user.ext_ids:
        response_json.external.append(Dict())
        ext_sub, ext_iss = get_sub_iss_by_identity(e.identity)
        response_json.external[-1].sub = ext_sub
        response_json.external[-1].iss = ext_iss
        response_json.external[-1].display_name = e.jsondata.display_name

    return JSONResponse(response_json)


@router_api.get("/{site}/get_mappings/{subiss}")
def get_mappings(request: Request, site: str, subiss: str):
    encoded_sub, encoded_iss = subiss.split("@")
    sub = unquote_plus(encoded_sub)
    iss = unquote_plus(encoded_iss)
    provider_name = get_provider_name_by_iss(iss)
    logger.debug(F"provider_name: {provider_name}")
    identity = f"{provider_name}:{sub}"
    user = DatabaseUser(site)
    session_id = user.get_session_id_by_user_id(identity)

    provider_name, sub = get_provider_name_sub_by_identity(identity)
    sub, iss = get_sub_iss_by_identity(identity)

    logger.info(f"Site:     {site}")
    logger.info(f"subiss:   {subiss}")
    logger.info(f"     sub: {sub}")
    logger.info(f"     iss: {iss}")
    logger.info(f"     iss: {iss}")
    logger.info(f"     provider_name: {provider_name}")
    logger.info(f"          identity: {identity}")
    logger.info(f"session_id:{session_id}")

    if not session_id:
        return JSONResponse({"message": "no such user"}, status_code=404)
    user.load_all_identities(session_id)
    # logger.debug(user.ext_ids)
    response_json = Dict()
    response_json.internal = user.int_id.identity
    response_json.external = []
    for e in user.ext_ids:
        response_json.external.append(e.identity)

    return fill_json_response(user)


@router_api.get("/{site}/get_mappings_by_id/{identity}")
def get_mappings_by_id(request: Request, site: str, identity: str):
    logger.info(f"Site:     {site}")
    logger.info(f"Identity: {identity}")

    user = DatabaseUser(site)
    session_id = user.get_session_id_by_user_id(identity, "external")
    logger.info(f"session_id:{session_id}")
    if not session_id:
        logger.info("no external entry found for user, tring internal")
        session_id = user.get_session_id_by_user_id(identity, "internal")
        logger.info(f"internal session_id:{session_id}")
        if not session_id:
            logger.info("no entry found for user")
            return JSONResponse({"message": "No linkage found for this user"})
            # raise exceptions.BadRequest({"message": "No linkage found for this user"})

    user.load_all_identities(session_id)
    # logger.debug(user.ext_ids)


@router_api.get("/{site}/get_mappings_by_id_raw/{identity}")
def get_mappings_by_id_raw(request: Request, site: str, identity: str):
    logger.info(f"Site:     {site}")
    logger.info(f"Identity: {identity}")

    user = DatabaseUser(site)
    session_id = user.get_session_id_by_user_id(identity, "external")
    logger.info(f"session_id:{session_id}")
    if not session_id:
        logger.info("no external entry found for user, tring internal")
        session_id = user.get_session_id_by_user_id(identity, "internal")
        logger.info(f"internal session_id:{session_id}")
        if not session_id:
            logger.info("no entry found for user")
            return JSONResponse({"message": "No linkage found for this user"})

    user.load_all_identities(session_id)
    # logger.debug(user.ext_ids)

    response = JSONResponse({"internal_id": user.int_id, "external_ids": user.ext_ids})
    return response


@router_api.get("/all_my_mappings_raw")
@flaat.is_authenticated()
def all_my_mappings_raw(request: Request):
    user_infos = flaat.get_user_infos_from_request(request)
    if user_infos is None:
        raise exceptions.InternalException("Could not find user infos")
    logger.info(user_infos.toJSON())
    logger.info(type(user_infos))
    response = JSONResponse({"key": "value"})
    return response


# from starlette.responses import RedirectResponse
# @router_api.get("/auth")
# def sim_auth(request: Request):
#     access_token = request.auth.jwt_create({
#         "id": 1,
#         "identity": "demo:1",
#         "image": None,
#         "display_name": "John Doe",
#         "email": "john.doe@auth.sim",
#         "username": "JohnDoe",
#         "exp": 3689609839,
#     })
#     response = RedirectResponse("/")
#     response.set_cookie(
#         "Authorization",
#         value=f"Bearer {access_token}",
#         max_age=request.auth.expires,
#         expires=request.auth.expires,
#         httponly=request.auth.http,
#     )
#     return response


if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(test, host="0.0.0.0", port=8000)
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(router_api, host="0.0.0.0", port=8000)

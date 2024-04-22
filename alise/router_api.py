# vim: tw=100 foldmethod=indent
# pylint: disable=logging-fstring-interpolation

# from fastapi import FastAPI
from urllib.parse import unquote_plus

from addict import Dict
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
import random
import string

from flaat.fastapi import Flaat
from fastapi import Depends, FastAPI, Request, Response
from fastapi.security import HTTPBasicCredentials, HTTPBearer

from alise.logsetup import logger
from alise import exceptions
from alise.oauth2_config import get_provider_name_by_iss
from alise.oauth2_config import get_provider_name_by_hash
from alise.oauth2_config import get_sub_iss_by_identity
from alise.oauth2_config import get_provider_name_sub_by_identity
from alise.oauth2_config import get_providers_long

from alise.models import DatabaseUser

VERSION = "1.0.5"
# app = FastAPI()
flaat = Flaat()
security = HTTPBearer()
router_api = APIRouter(prefix="/api/v1")

flaat.set_trusted_OP_list(
    [
        "https://aai.egi.eu/auth/realms/egi",
        "https://aai-demo.egi.eu/auth/realms/egi",
        "https://accounts.google.com/",
        "https://login.helmholtz.de/oauth2/",
    ]
)
flaat.set_verbosity(3)


def fill_json_response(user):
    response_json = Dict()
    int_sub, int_iss = get_sub_iss_by_identity(user.int_id.identity)
    response_json.internal.sub = int_sub
    response_json.internal.iss = int_iss
    response_json.internal.username = user.int_id.jsondata.generated_username
    response_json.internal.last_seen = user.int_id.last_seen
    response_json.internal.display_name = user.int_id.jsondata.display_name

    response_json.external = []
    for e in user.ext_ids:
        response_json.external.append(Dict())
        ext_sub, ext_iss = get_sub_iss_by_identity(e.identity)
        response_json.external[-1].sub = ext_sub
        response_json.external[-1].iss = ext_iss
        response_json.external[-1].last_seen = e.last_seen
        response_json.external[-1].display_name = e.jsondata.display_name

    headers = {"Cache-Control": "public", "max-age": "31536000", "x-alise-version": VERSION}
    # "Age": "xxxxxxxx",
    # "x-alise-user-last-seen": "",
    return JSONResponse(response_json, headers=headers)


def decode_input(encoded_sub, encoded_iss):
    sub = unquote_plus(encoded_sub)
    iss = unquote_plus(encoded_iss)
    provider_name = get_provider_name_by_iss(iss)
    if not provider_name:
        provider_name = get_provider_name_by_hash(iss)
    logger.debug(f"provider_name: {provider_name}")
    identity = f"{provider_name}:{sub}"
    logger.info(f"  sub:      '{sub}'")
    logger.info(f"  iss:      '{iss}'")
    logger.info(f"  provider: '{provider_name}'")
    logger.info(f"  identity: '{identity}'")

    return (sub, iss, provider_name, identity)


@router_api.get("/{site}/get_mappings/{subiss}")
def get_mappings_subiss(request: Request, site: str, subiss: str, apikey: str):
    encoded_sub, encoded_iss = subiss.split("@")
    logger.info(f"Site:     {site}")
    logger.info(f"subiss:   {subiss}")
    (sub, iss, provider_name, identity) = decode_input(encoded_sub, encoded_iss)

    user = DatabaseUser(site)
    if not user.apikey_valid(apikey):
        return JSONResponse(
            {"detail": [{"msg": "invalid apikey", "type": "invalid"}]}, status_code=401
        )

    session_id = user.get_session_id_by_user_id(identity)
    logger.info(f"session_id:{session_id}")

    if not session_id:
        return JSONResponse(
            {"detail": [{"msg": "no such user", "type": "not-mapped"}]}, status_code=401
        )
    user.load_all_identities(session_id)

    return fill_json_response(user)


@router_api.get("/target/{site}/mapping/issuer/{encoded_iss}/user/{encoded_sub}")
def get_mappings_path(request: Request, site: str, encoded_iss: str, encoded_sub: str, apikey: str):
    logger.info(f"Site:     {site}")
    (sub, iss, provider_name, identity) = decode_input(encoded_sub, encoded_iss)

    user = DatabaseUser(site)
    if not user.apikey_valid(apikey):
        return JSONResponse(
            {"detail": [{"msg": "invalid apikey", "type": "invalid"}]}, status_code=401
        )

    session_id = user.get_session_id_by_user_id(identity, "external")
    logger.info(f"session_id:{session_id}")

    if not session_id:
        return JSONResponse(
            {"detail": [{"msg": "no such user", "type": "not-mapped"}]}, status_code=401
        )

    user.load_all_identities(session_id)

    return fill_json_response(user)


@router_api.get("/version")
def version():
    return VERSION


@router_api.get("/authenticated")
@flaat.is_authenticated()
def authenticated(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
):
    user_infos = flaat.get_user_infos_from_request(request)
    return "This worked: there was a valid login"


@router_api.get("/all_my_mappings_raw")
# @flaat.is_authenticated()
def all_my_mappings_raw(
    request: Request,
):
    user_infos = flaat.get_user_infos_from_request(request)
    if user_infos is None:
        raise exceptions.InternalException("Could not find user infos")
    # logger.info(user_infos.toJSON())
    logger.info(type(user_infos))
    response = JSONResponse({"key": "value"})
    return response


def randomword(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


@router_api.get("/target/{site}/get_apikey")
@flaat.is_authenticated()
def get_apikey(
    request: Request,
    site: str,
):
    user_infos = flaat.get_user_infos_from_request(request)
    if user_infos is None:
        raise exceptions.InternalException("Could not find user infos")

    email = user_infos.get("email")
    username = user_infos.get("name")
    sub = user_infos.get("sub")
    iss = user_infos.get("iss")
    apikey = randomword(32)

    user = DatabaseUser(site)
    user.store_apikey(user_name=username, user_email=email, sub=sub, iss=iss, apikey=apikey)

    return JSONResponse({"apikey": apikey})


@router_api.get("/target/{site}/validate_apikey/{apikey}")
def validate_apikey(
    request: Request,
    site: str,
    apikey: str,
):
    user = DatabaseUser(site)
    if user.apikey_valid(apikey=apikey):
        return JSONResponse({"apikey": True})
    return JSONResponse({"apikey": False})


if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(test, host="0.0.0.0", port=8000)
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(router_api, host="0.0.0.0", port=8000)


@router_api.get("/alise/supported_issuers")
def list_supported_issuers(request: Request):
    supported_issuers = get_providers_long()
    headers = {"x-alise-version": VERSION}
    return JSONResponse({"supported_issuers": supported_issuers}, headers=headers)

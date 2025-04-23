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
import sqlite3

from flaat.fastapi import Flaat
from flaat.requirements import get_claim_requirement
from fastapi import Depends, FastAPI, Request, Response
from fastapi.security import HTTPBasicCredentials, HTTPBearer
import aarc_entitlement

from alise.logsetup import logger
from alise import exceptions
from alise.oauth2_config import get_provider_name_by_iss
from alise.oauth2_config import get_provider_name_by_hash
from alise.oauth2_config import get_sub_iss_by_identity
from alise.oauth2_config import get_provider_name_sub_by_identity
from alise.oauth2_config import get_providers_long

from alise.models import DatabaseUser
from alise.config import CONFIG

VERSION = "1.1.4"
# app = FastAPI()
flaat = Flaat()
security = HTTPBearer()
router_api = APIRouter(prefix="/api/v1")

trusted_OP_list = []
for op_name in CONFIG.auth.get_op_names():
    op_config = CONFIG.auth.get_op_config(op_name)
    trusted_OP_list.append(op_config.op_url)

logger.debug("Trusted OPs:")
for op in trusted_OP_list:
    logger.debug(f"  {op}")


flaat.set_trusted_OP_list(trusted_OP_list)
flaat.set_verbosity(3)


def fill_json_response(user):
    response_json = Dict()
    # logger.debug(F"user.int_id.identity: {user.int_id.identity}")
    int_sub, int_iss = get_sub_iss_by_identity(user.int_id.identity)
    response_json.internal.sub = int_sub
    response_json.internal.iss = int_iss
    response_json.internal.username = user.int_id.jsondata.generated_username
    response_json.internal.last_seen = user.int_id.last_seen
    response_json.internal.display_name = user.int_id.jsondata.display_name

    response_json.external = []
    for e in user.ext_ids:
        response_json.external.append(Dict())
        # logger.debug(F"e.identity: {e.identity}")
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

    try:
        user = DatabaseUser(site)
        if not user.apikey_valid(apikey):
            return JSONResponse(
                {"detail": [{"msg": "invalid apikey", "type": "invalid"}]}, status_code=401
            )

        session_id = user.get_session_id_by_user_id(identity, "external")
        if not session_id:
            return JSONResponse(
                {"detail": [{"msg": "no such user", "type": "not-mapped"}]}, status_code=401
            )

        user.load_all_identities(session_id)
        return fill_json_response(user)
    except Exception as E:
        # raise
        return JSONResponse({"error": str(E)})


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

def is_internal_site(sitename):
    op_conf = CONFIG.auth.get_op_config(sitename)
    if op_conf is None:
        return False
    op_internal = op_conf.internal
    return op_internal

@router_api.get("/{site}/all_my_mappings_raw")
# @flaat.is_authenticated()
def all_my_mappings_raw(
        request: Request, site: str
):
    try:
        user_infos = flaat.get_user_infos_from_request(request)
        logger.debug(F"user_infos:")
        logger.debug(user_infos)
        if user_infos is None:
            raise exceptions.InternalException("Could not find user infos")

        provider_short_name = get_provider_name_by_iss(user_infos.issuer)
        logger.debug(F"{provider_short_name=}")
        sub = user_infos.subject
        if not is_internal_site(site):
            raise exceptions.InternalException("Invalid site name")

        logger.debug(F"internal")
        user = DatabaseUser(site)
        logger.debug("got user")
        session_id = user.get_session_id_by_user_id(F"{provider_short_name}:{sub}")
        logger.debug("got session")

        try:
            user.load_all_identities(session_id)
        except sqlite3.ProgrammingError as e:
            raise exceptions.InternalException("No IDs linked")

        return fill_json_response(user)
    except Exception as E:
        # raise
        return JSONResponse({"error": str(E)})


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
    try:
        iss = user_infos.access_token_info.body["iss"]
    except:
        iss = ""
    iss_name = get_provider_name_by_iss(iss)
    if not iss_name:
        raise exceptions.BadRequest("Can only issue apikeys for OPs that issue jwt Access "\
                                    "Tokens. Among some, globus and google are known not to support this.")
    logger.debug(F"{iss=}")
    if user_infos is None:
        raise exceptions.BadRequest("Could not find user infos")

    # Get Authorisation config:
    op_conf = CONFIG.auth.get_op_config(iss_name)
    req_entitlements = op_conf.admin_entitlement
    req_claim = op_conf.admin_entitlement_claim
    at_entitlements = []
    ui_entitlements = []
    is_entitlements = []
    logger.debug(F"{iss_name=}")
    logger.debug(F"{req_claim=}")
    logger.debug(F"{req_entitlements=}")
    try:
        at_entitlements = user_infos.access_token_info.body[req_claim]
    except KeyError:
        logger.debug("at: keyerror")
        pass
    except TypeError:
        logger.debug("at: typeerror")
        pass
    try:
        ui_entitlements = user_infos.user_info[req_claim]
    except KeyError:
        logger.debug("ui: keyerror")
        pass
    except TypeError:
        logger.debug("ui: typeerror")
        pass
    try:
        is_entitlements = user_infos.introspection_info[req_claim]
    except KeyError:
        logger.debug("is: keyerror")
        pass
    except TypeError:
        logger.debug("is: typeerror")
        pass
    logger.debug(F"{at_entitlements=}")
    logger.debug(F"{ui_entitlements=}")
    logger.debug(F"{is_entitlements=}")
    if isinstance(at_entitlements, str):
        at_entitlements = [at_entitlements]
    if isinstance(ui_entitlements, str):
        ui_entitlements = [ui_entitlements]
    if isinstance(is_entitlements, str):
        is_entitlements = [is_entitlements]
    all_entitlements = at_entitlements + ui_entitlements + is_entitlements
    logger.debug(F"All Entitlements: \n{'\n'.join(all_entitlements)}")
    all_entitlements = [x.split('#')[0] for x in all_entitlements]
    #
    logger.debug(F"Entitlements: \n{'\n'.join(all_entitlements)}")

    # Check Authorisation:
    authorised = False
    for req_e in req_entitlements:
        if req_e in all_entitlements:
            authorised = True
    if not authorised:
        raise exceptions.Unauthorised("Not authorised")

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

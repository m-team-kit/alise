# from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse

from flaat.fastapi import Flaat
from alise.logsetup import logger

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


@router_api.get("/{site}/all_mappings_for_user/{identity}")
def all_mappings_for_user(request: Request, site: str, identity: str):
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

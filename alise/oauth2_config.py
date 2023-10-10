# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation

import os
import requests
from dotenv import load_dotenv

# from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2

# from social_core.backends.elixir import ElixirOpenIdConnect
from social_core.backends.open_id_connect import OpenIdConnectAuth

from fastapi_oauth2.claims import Claims
from fastapi_oauth2.config import OAuth2Config
from fastapi_oauth2.client import OAuth2Client

from alise.config import CONFIG
from alise.logsetup import logger
from alise import exceptions


CONFIG_KEY_MAP = {
    "ACCESS_TOKEN_URL": "token_endopint",
    "AUTHORIZATION_URL": "authorization_endpoint",
    "REVOKE_TOKEN_URL": "revocation_endpoint",
    "USERINFO_URL": "userinfo_endpoint",
    "JWKS_URI": "jwks_uri",
    # apparently not used: = rsp.json()["introspection_endpoint"]
}

logger.info(f"Loading dotenv from {CONFIG.oidc.oidc_config}")
if not load_dotenv(dotenv_path=CONFIG.oidc.oidc_config):
    raise exceptions.InternalException("Could not load dotenv")


# make sure OIDC_ENDPOINT is defined
class MyGoogleOAuth2(GoogleOAuth2):
    OIDC_ENDPOINT = os.getenv("GOOGLE_ISS", "")


class HelmholtzOpenIdConnect(OpenIdConnectAuth):
    name = "helmholtz"
    OIDC_ENDPOINT = os.getenv("HELMHOLTZ_ISS", "")
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "external"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(
        OIDC_ENDPOINT + "/.well-known/openid-configuration", timeout=15
    ).json()
    try:
        ACCESS_TOKEN_URL = autoconf["token_endpoint"]
        AUTHORIZATION_URL = autoconf["authorization_endpoint"]
        REVOKE_TOKEN_URL = autoconf["revocation_endpoint"]
        USERINFO_URL = autoconf["userinfo_endpoint"]
        JWKS_URI = autoconf["jwks_uri"]
    except KeyError as e:
        logger.error(f"Cannot find {e} for {name}")
    logger.debug(f"Initialised {name}")

    def setting(self, name, default=None):
        return getattr(self, name, default)


class EGIOpenIdConnect(OpenIdConnectAuth):
    name = "egi"
    OIDC_ENDPOINT = os.getenv("EGI_ISS", "")
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "external"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(
        OIDC_ENDPOINT + "/.well-known/openid-configuration", timeout=15
    ).json()
    try:
        ACCESS_TOKEN_URL = autoconf["token_endpoint"]
        AUTHORIZATION_URL = autoconf["authorization_endpoint"]
        REVOKE_TOKEN_URL = autoconf["revocation_endpoint"]
        USERINFO_URL = autoconf["userinfo_endpoint"]
        JWKS_URI = autoconf["jwks_uri"]
    except KeyError as e:
        logger.error(f"Cannot find {e} for {name}")
    logger.debug(f"Initialised {name}")

    def setting(self, name, default=None):
        return getattr(self, name, default)


class VegaKeycloakOpenIdConnect(OpenIdConnectAuth):
    name = "vega-kc"
    OIDC_ENDPOINT = os.getenv("VEGA_ISS", "")
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "internal"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(
        OIDC_ENDPOINT + "/.well-known/openid-configuration", timeout=15
    ).json()
    try:
        ACCESS_TOKEN_URL = autoconf["token_endpoint"]
        AUTHORIZATION_URL = autoconf["authorization_endpoint"]
        REVOKE_TOKEN_URL = autoconf["revocation_endpoint"]
        USERINFO_URL = autoconf["userinfo_endpoint"]
        JWKS_URI = autoconf["jwks_uri"]
    except KeyError as e:
        logger.error(f"Cannot find {e} for {name}")
    logger.debug(f"Initialised {name}")

    def setting(self, name, default=None):
        return getattr(self, name, default)


class FelsInternalOpenIdConnect(OpenIdConnectAuth):
    name = "kit-fels"
    OIDC_ENDPOINT = os.getenv("FELS_ISS", "")
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "internal"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(
        OIDC_ENDPOINT + "/.well-known/openid-configuration", timeout=15
    ).json()
    try:
        ACCESS_TOKEN_URL = autoconf["token_endpoint"]
        AUTHORIZATION_URL = autoconf["authorization_endpoint"]
        REVOKE_TOKEN_URL = autoconf["revocation_endpoint"]
        USERINFO_URL = autoconf["userinfo_endpoint"]
        JWKS_URI = autoconf["jwks_uri"]
    except KeyError as e:
        logger.error(f"Cannot find {e} for {name}")
    logger.debug(f"Initialised {name}")

    def setting(self, name, default=None):
        return getattr(self, name, default)


oauth2_config = OAuth2Config(
    allow_http=True,
    jwt_secret="secret",
    jwt_expires=900,
    jwt_algorithm="HS256",
    # jwt_secret=os.getenv("JWT_SECRET"),
    # jwt_expires=os.getenv("JWT_EXPIRES"),
    # jwt_algorithm=os.getenv("JWT_ALGORITHM"),
    clients=[
        OAuth2Client(
            backend=HelmholtzOpenIdConnect,
            client_id=os.getenv("HELMHOLTZ_CLIENT_ID", ""),
            client_secret=os.getenv("HELMHOLTZ_CLIENT_SECRET", ""),
            scope=[
                "openid",
                "profile",
                "email",
                "eduperson_assurance",
                "voperson_id",
                "iss",
            ],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
                # identity=lambda user: f"{quote_plus(os.getenv('HELMHOLTZ_ISS'))}@{quote_plus(user.sub)}",
            ),
        ),
        OAuth2Client(
            backend=EGIOpenIdConnect,
            client_id=os.getenv("EGI_CLIENT_ID", ""),
            client_secret=os.getenv("EGI_CLIENT_SECRET", ""),
            scope=["openid", "profile", "email", "eduperson_assurance"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
                # identity=lambda user: f"{os.getenv('EGI_ISS')}@{user.sub}",
            ),
        ),
        OAuth2Client(
            backend=MyGoogleOAuth2,
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
                # identity=lambda user: f"{os.getenv('GOOGLE_ISS', "")}@{user.sub}",
            ),
        ),
        OAuth2Client(
            backend=VegaKeycloakOpenIdConnect,
            client_id=os.getenv("VEGA_CLIENT_ID", ""),
            client_secret=os.getenv("VEGA_CLIENT_SECRET", ""),
            scope=[
                "openid",
                "profile",
                "email",
                "address",
                "microprofile-jwt",
                "roles",
                "web-origins",
                "offline_access",
                "phone",
                "acr",
            ],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
                generated_username=lambda user: f"{user.upn}",
                # identity=lambda user: f"{quote_plus(os.getenv('VEGA_ISS'))}@{quote_plus(user.sub)}",
            ),
        ),
        OAuth2Client(
            backend=FelsInternalOpenIdConnect,
            client_id=os.getenv("FELS_CLIENT_ID", ""),
            client_secret=os.getenv("FELS_CLIENT_SECRET", ""),
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
                generated_username=lambda user: f"{user.sub}",
                # identity=lambda user: f"{os.getenv('FELS_ISS')}@{user.sub}",
            ),
        ),
    ],
)


def get_provider_iss_by_name(name: str) -> str:
    for x in oauth2_config.clients:
        if x.backend.name == name:
            try:
                return x.backend.OIDC_ENDPOINT  # pyright: ignore
            except AttributeError:
                return ""
    return ""


def get_provider_name_by_iss(iss: str) -> str:
    for x in oauth2_config.clients:
        if x.backend.OIDC_ENDPOINT == iss:  # pyright: ignore
            return x.backend.name
    return ""


def get_sub_iss_by_identity(identity):
    provider_name, sub = identity.split(":")
    iss = get_provider_iss_by_name(provider_name)
    return (sub, iss)


def get_provider_name_sub_by_identity(identity):
    logger.debug(F"identity: {identity}")
    provider_name, sub = identity.split(":")
    return (provider_name, sub)


def get_providers(provider_type):
    names = []
    for x in oauth2_config.clients:
        try:
            if x.backend.provider_type == provider_type:  # pyright: ignore
                names.append(x.backend.name)
        except AttributeError:
            if provider_type == "external":  # external providers may not
                names.append(x.backend.name)  # explicitly define this attribute
    return names


def get_internal_providers():
    returnv = get_providers("internal")
    logger.info(f"internal providers: {returnv}")
    return returnv


def get_external_providers():
    return get_providers("external")

# vim: tw=100 foldmethod=indent

import requests

import os
from dotenv import load_dotenv

# from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2

# from social_core.backends.elixir import ElixirOpenIdConnect
from social_core.backends.open_id_connect import OpenIdConnectAuth

from fastapi_oauth2.claims import Claims
from fastapi_oauth2.config import OAuth2Config
from fastapi_oauth2.client import OAuth2Client

from alise.logsetup import logger


CONFIG_KEY_MAP = {
    "ACCESS_TOKEN_URL": "token_endopint",
    "AUTHORIZATION_URL": "authorization_endpoint",
    "REVOKE_TOKEN_URL": "revocation_endpoint",
    "USERINFO_URL": "userinfo_endpoint",
    "JWKS_URI": "jwks_uri",
    # apparently not used: = rsp.json()["introspection_endpoint"]
}

load_dotenv()

# make sure OIDC_ENDPOINT is defined
class MyGoogleOAuth2(GoogleOAuth2):
    OIDC_ENDPOINT = "https://accounts.google.com/"


class HelmholtzOpenIdConnect(OpenIdConnectAuth):
    name = "helmholtz"
    OIDC_ENDPOINT = "https://login.helmholtz.de/oauth2"
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "external"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(OIDC_ENDPOINT + "/.well-known/openid-configuration").json()
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
    OIDC_ENDPOINT = "https://aai.egi.eu/auth/realms/egi"
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "external"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(OIDC_ENDPOINT + "/.well-known/openid-configuration").json()
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
    OIDC_ENDPOINT = "https://sso.sling.si:8443/auth/realms/SLING"
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "internal"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(OIDC_ENDPOINT + "/.well-known/openid-configuration").json()
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
    OIDC_ENDPOINT = "https://fels.scc.kit.edu/oidc/realms/fels"
    ID_TOKEN_ISSUER = OIDC_ENDPOINT
    provider_type = "internal"

    # auto fill from .well-known/openid-configuration
    autoconf = requests.get(OIDC_ENDPOINT + "/.well-known/openid-configuration").json()
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
            client_id=os.getenv("HELMHOLTZ_CLIENT_ID"),
            client_secret=os.getenv("HELMHOLTZ_CLIENT_SECRET"),
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
            ),
        ),
        OAuth2Client(
            backend=EGIOpenIdConnect,
            client_id=os.getenv("EGI_CLIENT_ID"),
            client_secret=os.getenv("EGI_CLIENT_SECRET"),
            scope=["openid", "profile", "email", "eduperson_assurance"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
            ),
        ),
        OAuth2Client(
            backend=VegaKeycloakOpenIdConnect,
            client_id=os.getenv("VEGA_CLIENT_ID"),
            client_secret=os.getenv("VEGA_CLIENT_SECRET"),
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
            ),
        ),
        OAuth2Client(
            backend=FelsInternalOpenIdConnect,
            client_id=os.getenv("FELS_CLIENT_ID"),
            client_secret=os.getenv("FELS_CLIENT_SECRET"),
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
            ),
        ),
        OAuth2Client(
            backend=MyGoogleOAuth2,
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
            ),
        ),
    ],
)


def get_providers(provider_type):
    names = []
    for x in oauth2_config.clients:
        try:
            if x.backend.provider_type == provider_type:
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

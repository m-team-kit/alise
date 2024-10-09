# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation

import os
from sys import exit
import requests
from dotenv import load_dotenv
import hashlib

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


def make_oidc_config_class_google(op_name):
    class NewClass(GoogleOAuth2):
        OIDC_ENDPOINT = os.getenv("GOOGLE_ISS", "")
        provider_type = "external"

    return NewClass


def make_oidc_config_class(op_name, op_config):
    class NewClass(OpenIdConnectAuth):
        provider_type: str
        def setting(self, op_name, default=None):
            return getattr(self, op_name, default)

    try:
        ## Sonderlocke for google
        if op_config.op_url.startswith("https://accounts.google.com"):
            return make_oidc_config_class_google(op_name)

        NewClass.__name__ = op_name
        NewClass.name = op_name
        NewClass.name = op_name
        NewClass.OIDC_ENDPOINT = op_config.op_url
        NewClass.ID_TOKEN_ISSUER = NewClass.OIDC_ENDPOINT
        NewClass.provider_type = "external"
        if op_config.internal:
            NewClass.provider_type = "internal"
    except AttributeError as e:
        logger.warning(f"Cannot find attribute for {op_name}: {e}")

    ## Autoconf
    autoconf = requests.get(
        NewClass.OIDC_ENDPOINT + "/.well-known/openid-configuration", timeout=15
    ).json()
    try:
        NewClass.ACCESS_TOKEN_URL = autoconf["token_endpoint"]
        NewClass.AUTHORIZATION_URL = autoconf["authorization_endpoint"]
        NewClass.REVOKE_TOKEN_URL = autoconf["revocation_endpoint"]
        NewClass.USERINFO_URL = autoconf["userinfo_endpoint"]
        NewClass.JWKS_URI = autoconf["jwks_uri"]
    except KeyError as e:
        logger.warning(f"Cannot find {e} for {op_name}")
    return NewClass


def make_oidc_config(op_name):
    op_config = CONFIG.auth.get_op_config(op_name)
    backend = make_oidc_config_class(op_name, op_config)
    client = OAuth2Client(
        backend=backend,
        client_id=op_config.client_id,
        client_secret=op_config.client_secret,
        scope=op_config.scopes,
        claims=Claims(
            identity=lambda user: f"{user.provider}:{user.sub}",
            generated_username=lambda user: f"{user.get(op_config.username_claim)}",
        ),
    )
    return client


# vega:                generated_username=lambda user: f"{user.upn}",
# fels:                generated_username=lambda user: f"{user.sub}",


configured_clients = []
for op_name in CONFIG.auth.get_op_names():
    configured_clients.append(make_oidc_config(op_name))

oauth2_config = OAuth2Config(
    allow_http=True,
    jwt_secret="secret",
    jwt_expires=900,
    jwt_algorithm="HS256",
    clients=configured_clients,
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


def get_provider_name_by_hash(iss: str, hash_method="sha1") -> str:
    for x in oauth2_config.clients:
        for test_string in [
            x.backend.OIDC_ENDPOINT,  # pyright: ignore
            x.backend.OIDC_ENDPOINT + "\n",  # pyright: ignore
        ]:

            hash_function = getattr(hashlib, hash_method)()
            hash_function.update((test_string).encode())  # pyright: ignore
            hash = hash_function.hexdigest()
            # logger.debug(F"hash: {hash} - {iss} - {x.backend.OIDC_ENDPOINT.encode()}")
            if hash == iss:  # pyright: ignore
                return x.backend.name
    return ""


def get_sub_iss_by_identity(identity):
    provider_name, sub = identity.split(":")
    iss = get_provider_iss_by_name(provider_name)
    return (sub, iss)


def get_provider_name_sub_by_identity(identity):
    logger.debug(f"identity: {identity}")
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


def get_providers_long():
    providers = {"internal": [], "external": []}
    for x in oauth2_config.clients:
        try:
            provider_type = x.backend.provider_type  # pyright: ignore
        except AttributeError as e:
            logger.warning(e)
            provider_type = "external"
        provider_name = x.backend.name
        provider_iss = x.backend.OIDC_ENDPOINT  # pyright: ignore
        providers[provider_type].append({"name": provider_name, "iss": provider_iss})
    return providers


def get_internal_providers():
    returnv = get_providers("internal")
    logger.info(f"internal providers: {returnv}")
    return returnv


def get_external_providers():
    return get_providers("external")

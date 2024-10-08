[![PyPI Badge](https://img.shields.io/pypi/v/alise.svg)](https://pypi.python.org/pypi/alise)
[![Read the Docs](https://readthedocs.org/projects/alise/badge/?version=latest)](https://alise.readthedocs.io/en/latest/?version=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Account LInking SErvice

Tool to link accounts - developer documentation

## API Usage:

Note: `http` is an easier-to-use drop-in replacement for `curl`

### Get an API key:

To get an API Key you need to be authorized via openid connect. We use
this solely to record who (sub, iss, email, name) requested which api-key

```
http  https://alise.data.kit.edu/api/v1/target/vega-kc/get_apikey "Authorization: Bearer `oidc-token egi`"

  or 

curl  https://alise.data.kit.edu/api/v1/target/vega-kc/get_apikey  -H "Authorization: Bearer `oidc-token egi`" | jq .
```


### Get a mapping from external to internal user

Note that the issuer needs to be urlencoded twice.

```
http https://alise.data.kit.edu/api/v1/target/vega-kc/mapping/issuer/`urlencode.py <issuer>`/user/`urlencode.py <subject>`?apikey=<apikey>

  or 

curl https://alise.data.kit.edu/api/v1/target/vega-kc/mapping/issuer/`urlencode.py <issuer>`/user/`urlencode.py <subject>`?apikey=<apikey> | jq .
```

## Get an API-key

You need to be authenticated with an Access Token to get your API key.
Here we use the `oidc-agent` configuration named `egi`:
```
ALISE=https://alise.data.kit.edu/api/v1
APIKEY=$(curl -sH "Authorization: Bearer $(oidc-token egi)" ${ALISE}/target/vega-kc/get_apikey | jq -r .apikey
```

## Find linked IDs

```
ISSUER=https://aai-demo.egi.eu/auth/realms/egi
SUBJECT=d7a53cbe3e966c53ac64fde7355956560282158ecac8f3d2c770b474862f4756@egi.eu
curl  ${ALISE}/target/vega-kc/mapping/issuer/$(tools/hashencode.py ${ISSUER})/user/$(tools/urlencode.py ${SUBJECT})?apikey=$APIKEY |jq .
```

!!! Note: The issuer needs to be encoded TWICE, because otherwise some
    python framework tries to decode that URL, which will break my
    assumptions.

## Get list of supported providers

```
curl -v ${ALISE}/alise/supported_issuers
```

## Caching headers

Alise supports these headers in general, the latter two of which might be
used for caching

```
x-alise-version: 1.0.5-dev3
cache-control: public
max-age: 31536000
```

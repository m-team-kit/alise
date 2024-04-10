[![PyPI Badge](https://img.shields.io/pypi/v/alise.svg)](https://pypi.python.org/pypi/alise)
[![Read the Docs](https://readthedocs.org/projects/alise/badge/?version=latest)](https://alise.readthedocs.io/en/latest/?version=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-bronze-e6ae77)](https://api.eu.badgr.io/public/assertions/udGVwFI8Qe6J_dEYVo34BA "SQAaaS bronze badge achieved")

# Account LInking SErvice
Tool to link accounts 

## Installation
Account LInking SErvice is available on [PyPI](https://pypi.org/project/alise/). Install using `pip`:
```
pip install alise
```

You can also install from the git repository:
```
git clone https://github.com/marcvs/alise
pip install -e ./alise
```

# Using ALISE

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

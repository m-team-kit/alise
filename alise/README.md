[![PyPI Badge](https://img.shields.io/pypi/v/alise.svg)](https://pypi.python.org/pypi/alise)
[![Read the Docs](https://readthedocs.org/projects/alise/badge/?version=latest)](https://alise.readthedocs.io/en/latest/?version=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Account LInking SErvice
Tool to link accounts 

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



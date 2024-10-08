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

## Run locally (e.g. for testing)

```
# from the dir where alise is installed:
gunicorn alise.daemon:app
```

## Run as a service

### Nginx

We provide an nginx configuration file in `alise/etc/nginx.alise`. Simply
copy or it to nginx like:
```
ln -s $PWD/alise/etc/nginx.alise /etc/nginx/sites-enabled
```

## Systemd

We provide a systemd service file in `alise/etc/alise.service`. Simply
copy link it to systemd like:
```
ln -s $PWD/alise/etc/alise.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable alise.service
systemctl start alise.service
```


## Configuration

ALISE is configured via two files:

- `/etc/alise/alise.conf`: 
    - Logging
    - Location of `oidc.conf`
    - Template provided

- `/etc/alise/oidc.conf`
    - OIDC Providers
    - Template provided

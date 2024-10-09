[![PyPI Badge](https://img.shields.io/pypi/v/alise.svg)](https://pypi.python.org/pypi/alise)
[![Read the Docs](https://readthedocs.org/projects/alise/badge/?version=latest)](https://alise.readthedocs.io/en/latest/?version=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-bronze-e6ae77)](https://api.eu.badgr.io/public/assertions/udGVwFI8Qe6J_dEYVo34BA "SQAaaS bronze badge achieved")

# Account LInking SErvice

Tool to link accounts

## Installation

Account LInking SErvice is available on [PyPI](https://pypi.org/project/alise/). Install using `pip`:

```bash
pip install alise
```

You can also install from the git repository:

```bash
git clone https://github.com/marcvs/alise
pip install -e ./alise
```

### Dependencies

ALISE depends on gunicorn:

```bash
apt install gunicorn
```


## Run locally (e.g. for testing)

```bash
# from the dir where alise is installed:
gunicorn alise.daemon:app -k "uvicorn.workers.UvicornWorker"
```

Then point your browser to <http://localhost:8000>

## Run as a service

### Nginx

We provide an nginx configuration file in `alise/etc/nginx.alise`
([github](https://github.com/m-team-kit/alise/tree/master/alise/etc)). Simply
copy or it to nginx like:

```bash
ln -s $PWD/alise/etc/nginx.alise /etc/nginx/sites-enabled
```

### Systemd

We provide a systemd service file in `alise/etc/alise.service`
([github](https://github.com/m-team-kit/alise/tree/master/alise/etc)). Simply
copy link it to systemd like:

```bash
ln -s $PWD/alise/etc/alise.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable alise.service
systemctl start alise.service
```

### Static HTML

Place content of `alise/static` to place that nginx can serve as `/static`

### Icon

Place an icon of your site into `/static/<name of your sites config entry`.svg
(Yep that's a bit hacky)


## Configuration

ALISE is configured via a single config file. A template is provided in
`alise/etc/alise.conf`([github](https://github.com/m-team-kit/alise/tree/master/alise/etc)). It should be self-explanatory.


# vim: tw=100 foldmethod=indent

import logging
from logging.handlers import RotatingFileHandler
import sys

from alise.parse_args import args
from alise.config import CONFIG

# logger = logging.getLogger(__name__)
logger = logging.getLogger("")  # => This is the key to allow logging from other modules

DISPLAY_PATHLEN = 15


class PathTruncatingFormatter(logging.Formatter):
    """formatter for logging"""

    def format(self, record):
        pathname = record.pathname
        if len(pathname) > DISPLAY_PATHLEN:
            pathname = f"...{pathname[-(DISPLAY_PATHLEN+2):]}"
        record.pathname = pathname
        return super().format(record)


def setup_logging():
    """setup logging"""

    formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d]%(levelname)8s - %(message)s", datefmt="%H:%M:%S"
    )

    formatter = PathTruncatingFormatter(
        fmt=f"[%(asctime)s] [%(pathname){DISPLAY_PATHLEN}s:%(lineno)-4d]%(levelname)8s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # setup logfile
    try:
        logfile = args.logfile
    except AttributeError:
        logfile = None
    if logfile is None:
        logfile = CONFIG.messages.log_file
    if logfile:
        handler = RotatingFileHandler(logfile, maxBytes=10**6, backupCount=2)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # setup log level
    try:
        loglevel = args.loglevel
    except AttributeError:
        loglevel = None
    if loglevel is None:
        loglevel = CONFIG.messages.log_level
    if loglevel is None:
        loglevel = "INFO"
    logger.setLevel(loglevel)

    # turn off logging noise:
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("flask_pyoidc").setLevel(logging.ERROR)
    logging.getLogger("oic").setLevel(logging.ERROR)
    logging.getLogger("jwkest").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("flaat").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    return logger


logger = setup_logging()

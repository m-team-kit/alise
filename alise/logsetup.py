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
    my_level = logging.CRITICAL
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("flask_pyoidc").setLevel(my_level)
    logging.getLogger("oic").setLevel(my_level)
    logging.getLogger("jwkest").setLevel(my_level)
    logging.getLogger("urllib3").setLevel(my_level)
    logging.getLogger("werkzeug").setLevel(my_level)
    logging.getLogger("flaat").setLevel(my_level)
    logging.getLogger("httpx").setLevel(my_level)
    return logger


logger = setup_logging()

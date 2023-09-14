# vim: tw=100 foldmethod=indent

import logging
from logging.handlers import RotatingFileHandler
import sys

from alise.parse_args import args
from alise.config import CONFIG

# logger = logging.getLogger(__name__)
logger = logging.getLogger("")  # => This is the key to allow logging from other modules


class PathTruncatingFormatter(logging.Formatter):
    """formatter for logging"""

    def format(self, record):
        pathname = record.pathname
        if len(pathname) > 15:
            pathname = f"...{pathname[-17:]}"
        record.pathname = pathname
        return super().format(record)


def setup_logging():
    """setup logging"""

    formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d]%(levelname)7s - %(message)s", datefmt="%H:%M:%S"
    )

    formatter = PathTruncatingFormatter(
        fmt="[%(asctime)s] [%(pathname)15s:%(lineno)-3d]%(levelname)7s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # setup logilfe
    try:
        logfile = args.get("logfile")
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
        loglevel = args.get("loglevel")
    except AttributeError:
        loglevel = None
    if loglevel is None:
        logfile = CONFIG.messages.log_file
    if loglevel is None:
        loglevel = "INFO"
    print(f"loglevel: {loglevel}")
    logger.setLevel(loglevel)

    # turn off logging noise:
    for tool in ("werkzeug", "flaat", "urllib3"):
        other_log = logging.getLogger(tool)
        other_log.setLevel(logging.CRITICAL)
        other_log.addHandler(handler)

    return logger


logger = setup_logging()

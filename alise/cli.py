"""Console script for alise."""

# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation, unused-import

import sys
import logging
import alise.logsetup
from alise.config import CONFIG
from alise.parse_args import args


logger = logging.getLogger(__name__)


def main():
    """Console script for alise."""
    logger.debug("This is just a test for 'debug'")
    logger.info("This is just a test for 'info'")
    logger.warning("This is just a test for 'warning'")
    logger.error("This is just a test for 'error'")

    print(f"Config.test.your_config: {CONFIG['test']['your_config']}")
    print(f"Config.test.lists_example: {CONFIG['test']['lists_example']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

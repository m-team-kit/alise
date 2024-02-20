# vim: tw=100 foldmethod=indent
"""Parse commandline options"""

import argparse
import os
import sys


def parseOptions():
    """Parse commandline options"""

    # folder_of_executable = os.path.split(sys.argv[0])[0]
    basename = os.path.basename(sys.argv[0]).rstrip(".py")
    # dirname = os.path.dirname(__file__)
    # log_file = f"{dirname}/{basename}.log"
    # log_file = "cli.log"
    config_file = os.environ["HOME"] + f"/.config/{basename}.conf"

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--verbose", "-v", action="count", default=0, help="Verbosity")
    parser.add_argument("--debug", "-d", action="count", default=0, help="Logmode debug")
    parser.add_argument("--config", "-c", default=config_file, help="config file")
    parser.add_argument("--logfile", default=None, help="logfile")
    parser.add_argument("--loglevel", default=None)

    print("Replace this message by putting your code into alise.parse_args.py")
    return parser


# reparse args on import, unless pytest
if "_pytest" in sys.modules:
    args = {}
elif "uvicorn" in sys.modules:
    # print("ignoring args for uvicorn")
    args = {}
else:
    # print("args parsed")
    args = parseOptions().parse_args()
    print("WARNING: not parsing args, to support pytest")

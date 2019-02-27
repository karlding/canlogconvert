from __future__ import print_function

import argparse
import sys

from .subparsers import convert as _convert


def _main():
    parser = argparse.ArgumentParser(description="CAN Trace format converter")

    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument(
        "--version", action="version", version="1.0.0", help="Print version information"
    )

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    subparsers.required = True

    _convert.add_subparser(subparsers)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit("error: {}".format(e))

from __future__ import print_function

from ..traces import formats as trace_formats
from ..traces.formats import trc

import os


def _do_convert(args):
    """
    +-----------+--------------------+
    | Extension | Database format    |
    +===========+====================+
    | .trc      | PEAK CAN TRC       |
    +-----------+--------------------+
    | .asc      | ASCII logging file |
    +-----------+--------------------+
    """
    filename, file_extension = os.path.splitext(args.infile)

    # Register all Input Readers
    input_readers = {".trc": trace_formats.trc}

    with open(args.infile, "r") as fin:
        try:
            input_readers[file_extension].load_string(fin.read())
        except KeyError:
            raise Error("Unsupported input file extension '{}'".format(file_extension))

    # Then write the Internal Representation to the output format
    print(args.outfile)
    return


def add_subparser(subparsers):
    convert_parser = subparsers.add_parser(
        "convert", description="Convert given Trace from one format to another."
    )
    convert_parser.add_argument(
        "-I",
        metavar="infile",
        dest="infile",
        required=True,
        help="Input trace file (default stdin).",
    )
    convert_parser.add_argument(
        "-O",
        metavar="outfile",
        dest="outfile",
        required=True,
        help="Output trace file (default stdout).",
    )
    convert_parser.set_defaults(func=_do_convert)

"""Operations on a TRC file
"""
import pyparsing as pp
import pprint

from canlogconvert.traces.formats.internal_trace import InternalTrace
from canlogconvert.traces.formats.internal_trace import InternalMessage
from canlogconvert.traces.formats.internal_trace import InternalMessageDirection

#  pp.ParserElement.setDefaultWhitespaceChars(" \t")

# According to PEAK's "PEAK CAN TRC File Format" PDF document, these are the
# only valid version numbers supported
ValidVersions = pp.Or(
    pp.Literal("1.0")
    ^ pp.Literal("1.1")
    ^ pp.Literal("1.2")
    ^ pp.Literal("1.3")
    ^ pp.Literal("2.0")
    ^ pp.Literal("2.1")
)
FileVersion = (
    pp.Keyword(";$FILEVERSION")
    + pp.Literal("=")
    + pp.Combine(ValidVersions).setResultsName("FileVersion")
    + pp.LineEnd()
)
StartTime = (
    pp.Keyword(";$STARTTIME")
    + pp.Literal("=")
    + pp.Combine(
        pp.ZeroOrMore(pp.Word(pp.nums))
        + pp.Literal(".")
        + pp.ZeroOrMore(pp.Word(pp.nums))
    ).setResultsName("StartTime")
    + pp.LineEnd()
)
Columns = (
    pp.Keyword(";$COLUMNS")
    + pp.Literal("=")
    + pp.Group(
        pp.Combine(
            # Message Number
            pp.Optional(pp.Literal("N") + pp.Literal(","))
            # Time Offset (ms)
            + pp.Literal("O")
            + pp.Literal(",")
            # Type
            + pp.Literal("T")
            + pp.Literal(",")
            # Bus (1-16)
            # If Bus column is included, for events the Bus number can be specified as
            # '-' if the event is not associated with a specific bus
            + pp.Optional(pp.Literal("B") + pp.Literal(","))
            # CAN-ID (Hex)
            # 4 digits for 11-bit CAN-IDs (0000-07FF).
            # 8 digits for 29-bit CAN-IDs (00000000-1FFFFFFF).
            # Contains '-' for the message types EC, ER, ST, see 'T' column.
            + pp.Literal("I")
            + pp.Literal(",")
            # Direction.
            # Indicates whether the message was received ('Rx') or transmitted ('Tx').
            + pp.Literal("d")
            + pp.Literal(",")
            + pp.Optional(pp.Literal("R") + pp.Literal(","))
            + pp.oneOf("l L")
            + pp.Literal(",")
            + pp.Literal("D")
        )
    ).setResultsName("Columns", listAllMatches=True)
    + pp.LineEnd()
)

StartTimeComment = pp.Literal(";") + pp.Literal("Start time: ")

StartTimeLineComment = (
    StartTimeComment
    + pp.Combine(
        pp.Combine(
            pp.Word(pp.nums)
            + pp.Literal("-")
            + pp.Word(pp.nums)
            + pp.Literal("-")
            + pp.Word(pp.nums)
        )
        + pp.Combine(
            pp.Word(pp.nums)
            + pp.Literal(":")
            + pp.Word(pp.nums)
            + pp.Literal(":")
            + pp.Word(pp.nums)
            + pp.Literal(".")
            + pp.Word(pp.nums)
            + pp.Literal(".")
            + pp.Word(pp.nums)
        ),
        joinString=" ",
        # TODO: Fix this hack
        adjacent=False,
    ).setResultsName("StartTimeLineComment")
    + pp.LineEnd()
)

LineComment = pp.Group(
    pp.NotAny(pp.Or(FileVersion ^ StartTime ^ Columns ^ StartTimeLineComment))
    + pp.Literal(";")
    + pp.Regex(r".*")
    + pp.LineEnd()
).setResultsName("LineComment", listAllMatches=True)


Header = FileVersion + StartTime + Columns

# [N],O,T,[B],I,d,[R],l/L,D
ColumnBusNumber = pp.Or(
    pp.Literal("1")
    ^ pp.Literal("2")
    ^ pp.Literal("3")
    ^ pp.Literal("4")
    ^ pp.Literal("5")
    ^ pp.Literal("6")
    ^ pp.Literal("7")
    ^ pp.Literal("8")
    ^ pp.Literal("9")
    ^ pp.Literal("10")
    ^ pp.Literal("11")
    ^ pp.Literal("12")
    ^ pp.Literal("13")
    ^ pp.Literal("14")
    ^ pp.Literal("15")
    ^ pp.Literal("16")
    ^ pp.Literal("-")
)

ColumnDirection = pp.Or(pp.Literal("Rx") ^ pp.Literal("Tx"))

ColumnData = pp.Optional(pp.Word(pp.hexnums)) + pp.ZeroOrMore(
    pp.Literal(" ") + pp.Word(pp.hexnums)
)
#  ColumnCanId = pp.Literal()

ColumnMessageType = pp.Or(
    pp.Literal("DT")
    ^ pp.Literal("FD")
    ^ pp.Literal("FB")
    ^ pp.Literal("FE")
    ^ pp.Literal("BI")
    ^ pp.Literal("RR")
    ^ pp.Literal("ST")
    ^ pp.Literal("EC")
    ^ pp.Literal("ER")
)

ColumnMessageNumber = pp.Word(pp.nums)

ColumnTimeOffset = pp.Combine(pp.Word(pp.nums) + pp.Literal(".") + pp.Word(pp.nums))

ColumnArbitrationID = pp.Combine(pp.OneOrMore(pp.Word(pp.hexnums)))

ColumnReserved = pp.Literal("-")
ColumnDLC = pp.Word(pp.nums)
ColumnData = pp.Combine(
    pp.Optional(pp.Word(pp.hexnums))
    + pp.ZeroOrMore(pp.Literal(" ") + pp.Word(pp.hexnums))
)

LineData = pp.Group(
    ColumnMessageNumber.setResultsName("ColumnMessageNumber")
    + ColumnTimeOffset.setResultsName("ColumnTimeOffset")
    + ColumnMessageType.setResultsName("ColumnMessageType")
    + ColumnBusNumber.setResultsName("ColumnBusNumber")
    + ColumnArbitrationID.setResultsName("ColumnArbitrationID")
    + ColumnDirection.setResultsName("ColumnDirection")
    + ColumnReserved.setResultsName("ColumnReserved")
    + ColumnDLC.setResultsName("ColumnDLC")
    + ColumnData.setResultsName("ColumnData")
    + pp.LineEnd()
).setResultsName("LineData", listAllMatches=True)

TrcFileFormat = Header + pp.ZeroOrMore(
    pp.Or(LineComment ^ LineData ^ StartTimeLineComment)
)

# T: Type of message
class TraceMessageType:
    # CAN or J1939 data frame
    CAN_DATA_FRAME = "DT"
    # CAN FD data frame
    CAN_FD_FRAME = "FD"
    # CAN FD data frame with BRS bit set (Bit Rate Switch)
    CAN_FD_BRS_FRAME = "FB"
    # CAN FD data frame with ESI bit set (Error State Indicator)
    CAN_FD_ESI_FRAME = "FE"
    # CAN FD data frame with both BRS and ESI bits set
    CAN_FD_BRS_ESI_FRAME = "BI"
    # Remote Request Frame
    RTR_FRAME = "RR"
    # Hardware Status change
    HW_STATUS_CHANGE = "ST"
    # Error Counter change
    ERROR_COUNTER_CHANGE = "EC"
    # Error Frame
    ERROR_FRAME = "ER"
    # Event. User-defined text, begins directly after bus specifier.
    EVENT = "EV"


# B: Bus (1-16), optional. If Bus column is included, for events the Bus
# number can be specified as '-' if the event is not associated with a specific
# bus.

# I: CAN-ID (Hex)
# 4 digits for 11-bit CAN-IDs (0000-07FF).
# 8 digits for 29-bit CAN-IDs (00000000-1FFFFFFF).
# Contains '-' for the message types EC, ER, ST, see 'T' column

# d: Direction. Indicates whether the message was received ('Rx') or transmitted ('Tx').
class Direction:
    DIRECTION_TX = "Tx"
    DIRECTION_RX = "Rx"


# R: Reserved. Only used for J1939 protocol. Contains '-' for CAN busses. For
# J1939 protocol, contains destination address of a Transport Protocol PDU2
# Large Message. Optional for files that contain only CAN or CAN FD frames.

# l: Data Length (0-1785). This is the actual number of data bytes, not the
# Data Length Code (0..15). Optional. If omitted, the Data Length Code column
# ('L') must be included.

# L: Data Length Code (CAN: 0..8; CAN FD: 0..15; J1939: 0..1785).
# Optional. If omitted, the Data Length column ('l') must be included

# D: Data. 0-1785 data bytes in hexadecimal notation.
# For Data Frames (message types DT, FD, FB, FE, BI, see 'T' column): Data
# bytes of message, if Data Length is > 0.
# Empty for Remote Request frames (message type RR).
# For Hardware Status changes (message type ST): 4-byte status code in Motorola
# format.
# For Error Frames (message type ER): 5 bytes of Error Frame data, see Error
# Frames under Version 2.0.
# For Error Counter changes (message type EC): 2 bytes of Error Counter data.
# The first byte contains the RX Error counter, the second byte the TX Error
# counter.


"""

    +---------+-------------------+--------------------------+
    | Version | File header       | Used by                  |
    +=========+===================+==========================+
    | 1.0     | -                 | PCAN-Explorer 3.0        |
    |         |                   | PCAN-Trace 1.0           |
    +---------+-------------------+--------------------------+
    | 1.1     | ;$FILEVERSION=1.1 | PCAN-Explorer 3.0.2      |
    |         |                   | PCAN-Explorer 4          |
    |         |                   | PCAN-Trace 1.5           |
    |         |                   | PCAN-View 3              |
    +---------+-------------------+--------------------------+
    | 1.2     | ;$FILEVERSION=1.2 | PCAN-Explorer 5.0 Beta 1 |
    +---------+-------------------+--------------------------+
    | 1.3     | ;$FILEVERSION=1.3 | PCAN-Explorer 5          |
    +---------+-------------------+--------------------------+
    | 2.0     | ;$FILEVERSION=2.0 | PCAN-View 4              |
    +---------+-------------------+--------------------------+
    | 2.1     | ;$FILEVERSION=2.1 | PCAN-Explorer 6          |
    +---------+-------------------+--------------------------+

Currently we only support TRC
"""

FILE_HEADER_VERSION_1_1 = ";$FILEVERSION=1.1"
FILE_HEADER_VERSION_1_2 = ";$FILEVERSION=1.2"
FILE_HEADER_VERSION_1_3 = ";$FILEVERSION=1.3"
FILE_HEADER_VERSION_2_0 = ";$FILEVERSION=2.0"
FILE_HEADER_VERSION_2_1 = ";$FILEVERSION=2.1"


def _resolve_trc_version(lines):
    if len(lines):
        if lines[0] == FILE_HEADER_VERSION_1_1:
            return "1.1"
        elif lines[0] == FILE_HEADER_VERSION_1_2:
            return "1.2"
        elif lines[0] == FILE_HEADER_VERSION_1_3:
            return "1.3"
        elif lines[0] == FILE_HEADER_VERSION_2_0:
            return "2.0"
        elif lines[0] == FILE_HEADER_VERSION_2_1:
            return "2.1"

    # Otherwise we assume this is 1.0
    return "1.0"


def _parse_starttime(lines):
    # $STARTTIME keyword to store the absolute start time of the trace file
    #
    # Integral part = Number of days that have passed since 12/30/1899
    # Fractional Part = Fraction of a 24-hour day that has elapsed, resolution
    # is 1 millisecond.
    #
    # ;$STARTTIME=43474.7738065227
    # COMMA $ = NUMBER+ PERIOD NUMBER+
    return


def _load_version(tokens):
    return tokens.get("FileVersion")


def _load_start_time(tokens):
    return tokens.get("StartTime")


def _load_start_time_comment(tokens):
    return tokens.get("StartTimeLineComment")


def _load_columns(tokens):
    return tokens.get("Columns")


def _load_message_arbitration_id(message):
    return int(message.get("ColumnArbitrationID"), 16)


def _load_message_dlc(message):
    return int(message.get("ColumnDLC"))


def _load_message_data(message):
    return bytearray.fromhex(message.get("ColumnData"))


def _load_message_direction(message):
    direction = message.get("ColumnDirection")
    direction_lookup = {
        "Rx": InternalMessageDirection.RX,
        "Tx": InternalMessageDirection.TX,
    }

    if direction in direction_lookup:
        return direction_lookup[direction]
    raise ValueError("Unsupported Direction")


def _load_rows(tokens):
    result = []
    for message in tokens.get("LineData"):
        msg = InternalMessage(
            arbitration_id=_load_message_arbitration_id(message),
            data=_load_message_data(message),
            dlc=_load_message_dlc(message),
            direction=_load_message_direction(message),
            timestamp=message.get("ColumnTimeOffset"),
        )
        result.append(msg)
    return result


def load_string(string):
    """Parse the given string

    Args:
        string (str): a string containing the TRC file's contents

    Returns:
        InternalTrace
    """
    tokens = TrcFileFormat.parseString(string)
    if not _load_version(tokens) == "2.1":
        raise ValueError("We only support 2.1", _load_version(tokens))

    messages = _load_rows(tokens)
    start_time = _load_start_time_comment(tokens)
    #  print(tokens.get("StartTimeLineComment"))

    return InternalTrace(messages=messages, start_timestamp=start_time)

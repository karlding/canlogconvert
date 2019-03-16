"""Internal representation of a CAN trace.
"""

from jinja2 import Environment, PackageLoader, select_autoescape
import datetime


class InternalMessageDirection(object):
    RX = 1
    TX = 2


class InternalMessageType(object):
    """
    Attributes:
        DT: CAN or J1939 data frame
        FD: CAN FD data frame
        FB: CAN FD data frame with BRS bit set (Bit Rate Switch)
        FE: CAN FD data frame with ESI bit set (Error State Indicator)
        BI: CAN FD data frame with both BRS and ESI bits set
        RR: Remote Request Frame
        ST: Hardware Status change
        EC: Error Counter change
        ER: Error Frame
        EV: Event. User-defined text, begins directly after bus specifier.
    """

    DT = 1
    FD = 2
    FB = 3
    FE = 4
    BI = 5
    RR = 6
    ST = 7
    EC = 8
    ER = 9
    EV = 10


class InternalMessage(object):
    """
    """

    def __init__(self, arbitration_id, data, dlc, direction, timestamp):
        """Create a new TraceMessage"""
        self._arbitration_id = arbitration_id
        self._data = data
        self._dlc = dlc
        self._direction = direction
        self._timestamp = timestamp
        self._message_type = InternalMessageType.DT
        self._bus_number = 1

    @property
    def arbitration_id(self):
        """int: the frame identifier used for arbitration on the bus.

        """
        return self._arbitration_id

    @arbitration_id.setter
    def arbitration_id(self, arbitration_id):
        self._arbitration_id = arbitration_id

    @property
    def data(self):
        """bytearray: a bytearray containing the CAN data"""
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def data_as_trc_string(self):
        return " ".join(["{:02X}".format(x) for x in self._data])

    @property
    def dlc(self):
        """int: the length of the CAN message"""
        return self._dlc

    @dlc.setter
    def dlc(self, dlc):
        self._dlc = dlc

    @property
    def direction(self):
        """InternalMessageDirection: the direction of the CAN message"""
        return self._direction

    @direction.setter
    def direction(self, direction):
        self._direction = direction

    @property
    def direction_as_trc_string(self):
        direction_to_str_lookup = {
            InternalMessageDirection.RX: "Rx",
            InternalMessageDirection.TX: "Tx",
        }
        return direction_to_str_lookup[self._direction]

    @property
    def timestamp(self):
        """when the messages was received"""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    @property
    def bus(self):
        """The CAN bus that this message was received on"""
        return self._bus

    @bus.setter
    def bus(self, bus):
        self._bus = bus

    @property
    def message_type(self):
        return self._message_type

    @property
    def message_type_as_trc_string(self):
        message_type_to_str_lookup = {
            InternalMessageType.DT: "DT",
            InternalMessageType.FD: "FD",
            InternalMessageType.FB: "FB",
            InternalMessageType.FE: "FE",
            InternalMessageType.BI: "BI",
            InternalMessageType.RR: "RR",
            InternalMessageType.ST: "ST",
            InternalMessageType.EC: "EC",
            InternalMessageType.ER: "ER",
            InternalMessageType.EV: "EV",
        }
        return message_type_to_str_lookup[self._message_type]

    @message_type.setter
    def message_type(self, message_type):
        self._message_type = message_type

    @property
    def bus_number(self):
        return self._bus_number


class InternalTrace(object):
    """
    Internal traces

    Attributes:
        messages (list)
    """

    def __init__(self, start_timestamp, messages):
        """Create a new InternalTrace

        Args:
            messages (list): a list of messages
        """
        self._start_timestamp = start_timestamp
        self._messages = messages
        self._buses = [1]

    @property
    def start_timestamp(self):
        return self._start_timestamp

    @start_timestamp.setter
    def start_timestamp(self, start_timestamp):
        self._start_timestamp = start_timestamp

    @property
    def messages(self):
        """list: a list of messages"""
        return self._messages

    @messages.setter
    def messages(self, messages):
        self._messages = messages

    def as_trc_string(self):
        """Convert to a TRC file

        Returns:
            str: a string representing a TRC file
        """
        env = Environment(loader=PackageLoader("canlogconvert", "templates"))
        template = env.get_template("trc.j2")

        return template.render(
            trc={
                "file_version": "2.1",
                "days_since_epoch": (
                    datetime.date(2019, 5, 4) - datetime.date(1899, 12, 30)
                ).days,
                "fractional_elapsed_day_ms": 1,
                "start_timestamp": self._start_timestamp,
            },
            messages=self._messages,
        )

    def as_log_string(self):
        """Convert to a log file

        Returns:
            str: a string representing a log file
        """
        return self._messages

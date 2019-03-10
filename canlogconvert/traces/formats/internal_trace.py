"""Internal representation of a CAN trace.
"""

from jinja2 import Environment, PackageLoader, select_autoescape
import datetime


class InternalMessage(object):
    """
    """

    def __init__(self, arbitration_id, data, dlc, timestamp):
        """Create a new TraceMessage"""
        self._arbitration_id = arbitration_id
        self._data = data
        self._dlc = dlc
        self._timestamp = timestamp

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
    def dlc(self):
        """int: the length of the CAN message"""
        return self._dlc

    @dlc.setter
    def dlc(self, dlc):
        self._dlc = dlc

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


class InternalTrace(object):
    """
    Internal traces

    Attributes:
        messages (list)
    """

    def __init__(self, messages):
        """Create a new InternalTrace

        Args:
            messages (list): a list of messages
        """
        self._messages = messages

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
                    datetime.date.today() - datetime.date(1899, 12, 30)
                ).days,
                "fractional_elapsed_day_ms": 1,
            }
        )

    def as_log_string(self):
        """Convert to a log file

        Returns:
            str: a string representing a log file
        """
        return self._messages

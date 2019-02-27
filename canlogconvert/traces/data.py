class MessageType:
    CAN_DATA_FRAME = 0
    # CAN FD data frame
    CAN_FD_FRAME = 1
    # CAN FD data frame with BRS bit set (Bit Rate Switch)
    CAN_FD_BRS_FRAME = 2
    # CAN FD data frame with ESI bit set (Error State Indicator)
    CAN_FD_ESI_FRAME = 3
    # CAN FD data frame with both BRS and ESI bits set
    CAN_FD_BRS_ESI_FRAME = 4
    # Remote Request Frame
    RTR_FRAME = 5
    # Hardware Status change
    HW_STATUS_CHANGE = 6
    # Error Counter change
    ERROR_COUNTER_CHANGE = 7
    # Error Frame
    ERROR_FRAME = 8
    # Event. User-defined text, begins directly after bus specifier.
    EVENT = 9


class CanMessageDirection:
    RX = 0
    TX = 1


class TraceData:
    # (time offset since start, CAN network, CAN id in decimal, [rx,tx], d, dlc, data bytes in hex)
    def __init__(
        self,
        offset,
        can_id,
        dlc,
        data,
        message_type=MessageType.CAN_DATA_FRAME,
        bus=None,
        direction=CanMessageDirection.RX,
    ):
        self._offset_us = offset
        self._message_type = message_type
        self._bus = bus
        self._can_id = can_id
        self._direction = direction
        self._reserved = reserved
        self._dlc = dlc
        self._data = data


class Traces:
    def __init__(self):
        # TraceData[]
        self._data = []

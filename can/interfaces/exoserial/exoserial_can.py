"""
A text based interface. For example use over serial ports like
"/dev/ttyS1" or "/dev/ttyUSB0" on Linux machines or "COM1" on Windows.
The interface is a simple implementation that has been used for
recording CAN traces.
"""

import logging, struct, crcengine
from can import BusABC, ExoMessage

logger = logging.getLogger("can.exoserial")

try:
    import serial
except ImportError:
    logger.warning(
        "You won't be able to use the serial can backend without "
        "the serial module installed!"
    )
    serial = None

try:
    from serial.tools import list_ports
except ImportError:
    list_ports = None


class ExoSerialBus(BusABC):
    """
    Enable basic can communication over a serial device with ExoTerras custom packet design.

    .. note:: See :meth:`can.interfaces.serial.ExoSerialBus._recv_internal`
              for some special semantics.

    """

    def __init__(
        self, channel, baudrate=115200, timeout=0.1, rtscts=False, *args, **kwargs
    ):
        """
        :param str channel:
            The serial device to open. For example "/dev/ttyS1" or
            "/dev/ttyUSB0" on Linux or "COM1" on Windows systems.

        :param int baudrate:
            Baud rate of the serial device in bit/s (default 115200).

            .. warning::
                Some serial port implementations don't care about the baudrate.

        :param float timeout:
            Timeout for the serial device in seconds (default 0.1).

        :param bool rtscts:
            turn hardware handshake (RTS/CTS) on and off

        """
        if not channel:
            raise ValueError("Must specify a serial port.")

        self.channel_info = "ExoSerial interface: " + channel
        self.ser = serial.serial_for_url(
            channel, baudrate=baudrate, timeout=timeout, rtscts=rtscts
        )

        super().__init__(channel=channel, *args, **kwargs)

    def shutdown(self):
        """
        Close the serial interface.
        """
        self.ser.close()

    def send(self, msg:ExoMessage, timeout=None):
        """
        Send a message over the serial device in ExoTerra RS-485 Format.

        :param can.Message msg:
            Message to send.

            .. note:: Flags like ``extended_id``, ``is_remote_frame`` and
                      ``is_error_frame`` will be ignored.

            .. note:: If the timestamp is a float value it will be converted
                      to an integer.

        :param timeout:
            This parameter will be ignored. The timeout value of the channel is
            used instead.

        """
        # try:
        #     timestamp = struct.pack("<I", int(msg.timestamp * 1000))
        # except struct.error:
        #     raise ValueError("Timestamp is out of range")
        # try:
        #     a_id = struct.pack("<I", msg.arbitration_id)
        # except struct.error:
        #     raise ValueError("Arbitration Id is out of range")
        print("===============CALLING EXOTERRA SEND===============")
        byte_msg = bytearray()
        #generate the 5bit header
        byte0 = (0x15 & 0x1F)
        #combine with cob-id
        byte0 |= (msg.node_cob_id & 0x07) << 5
        byte1 = (msg.node_cob_id >> 3)
        #add control bits
        byte2 = (msg.remote_transmission_request & 0x1) #1 bit
        byte2 |= (msg.identifier_extension_bit & 0x1) << 1 #1 bit
        byte2 |= (msg.reserved_bits & 0x2) << 2 #2 bits
        byte2 |= (msg.data_length & 0x4) << 4 #4bits
        #append all of the data
        byte_msg.append(byte0)
        byte_msg.append(byte1)
        byte_msg.append(byte2)
        byte_msg.extend(msg.data)
        #calc the crc
        #crcobj = crcengine.new("crc16-ibm")
        #crc = crcobj.calculate(byte_msg)
        #append crc

        byte_msg.extend(bytearray(crc))

        self.ser.write(byte_msg)

    def _recv_internal(self, timeout):
        """
        Read a message from the serial device.

        :param timeout:

            .. warning::
                This parameter will be ignored. The timeout value of the channel is used.

        :returns:
            Received message and False (because not filtering as taken place).

            .. warning::
                Flags like is_extended_id, is_remote_frame and is_error_frame
                will not be set over this function, the flags in the return
                message are the default values.

        :rtype:
            Tuple[can.Message, Bool]
        """
        try:
            # ser.read can return an empty string
            # or raise a SerialException
            rx_byte = self.ser.read()
        except serial.SerialException:
            return None, False

        if rx_byte and ord(rx_byte) == 0xAA:
            s = bytearray(self.ser.read(4))
            timestamp = (struct.unpack("<I", s))[0]
            dlc = ord(self.ser.read())

            s = bytearray(self.ser.read(4))
            arb_id = (struct.unpack("<I", s))[0]

            data = self.ser.read(dlc)

            rxd_byte = ord(self.ser.read())
            if rxd_byte == 0xBB:
                # received message data okay
                msg = Message(
                    timestamp=timestamp / 1000,
                    arbitration_id=arb_id,
                    dlc=dlc,
                    data=data,
                )
                return msg, False

        else:
            return None, False

    def fileno(self):
        if hasattr(self.ser, "fileno"):
            return self.ser.fileno()
        # Return an invalid file descriptor on Windows
        return -1

    @staticmethod
    def _detect_available_configs():
        channels = []
        serial_ports = []

        if list_ports:
            serial_ports = list_ports.comports()

        for port in serial_ports:
            channels.append({"interface": "serial", "channel": port.device})
        return channels

"""
A text based interface. For example use over serial ports like
"/dev/ttyS1" or "/dev/ttyUSB0" on Linux machines or "COM1" on Windows.
The interface is a simple implementation that has been used for
recording CAN traces.
"""

UDP_HOST = "127.0.0.1"
UDP_PORT = 8082 

import logging, struct, crcengine, time, platform, socket
from ..receiver import *
from can import BusABC, Message
from queue import Queue

logger = logging.getLogger("can.exoserial")
from loguru import logger as loguru_logger

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


class ExoSocketBus(BusABC):
    """
    Enable basic can communication over a serial device with ExoTerras custom packet design.

    .. note:: See :meth:`can.interfaces.serial.ExoSocketBus._recv_internal`
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
        print("THE SOCKET HAS ARRIVED!!!")        
        if not channel:
            raise ValueError("Must specify a serial port.")

        self.channel_info = "ExoSerial interface: " + channel

        print("EXOINTERFACE")
        #wait a second for the serial port to clear
        time.sleep(0.1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # UDP
        self.sock.connect((UDP_HOST, UDP_PORT))
        super().__init__(channel=channel, *args, **kwargs)

    def shutdown(self):
        """
        Close the serial interface.
        """
        #ae 22 08 40 00 22 02 00 00 00 00 8a f8

    def get_int_q(self):
        return self.int_q

    def send(self, msg:Message, timeout=None, data_size=8):
        """
        Takes in a message object and converts it to the ExoTerra RS-485 format, and then sends it
        :param can.Message msg:
            Message to send.
        :param timeout:
            This parameter will be ignored.
        """
        if data_size > 8:
            data_size = 8 #the max size is 8 bytes
        byte_msg = bytearray()
        #generate the 5bit header
        byte0 = (0xa8)
        #combine with top 3 bits cob-id
        byte0 |= (msg.arbitration_id & 0x700) >> 8
        byte1 = (msg.arbitration_id & 0xFF) #add rest of cob id
        #add control bits
        byte2 = (msg.is_remote_frame & 0x1) << 7 #rtr
        byte2 |= (msg.is_extended_id & 0x1) << 6 #ide
        byte2 |= (0 & 0x2) << 4 # reserved bits
        byte2 |= (data_size & 0xF) # data length
        #append all of the data
        byte_msg.append(byte0)
        byte_msg.append(byte1)
        byte_msg.append(byte2)
        #move the msg data to the byte_msg and make sure its 8 bytes
        msg_data = bytearray(8)
        for i,v in enumerate(msg.data):
            if i < 8:
                msg_data[i] = v
        byte_msg.extend(msg_data)
        #calc and append the crc
        crcobj = crcengine.new("crc16-ibm")
        crc = crcobj.calculate(byte_msg).to_bytes(2, byteorder="little") #might need to be switched to big, not sure yet
        byte_msg.extend(crc)
        #sendit!
        # print(f"sending: {str(byte_msg.hex())} len: {len(byte_msg)}")
        sock_data = bytearray()
        sock_data.extend(byte_msg)
        self.sock.sendto(sock_data, (UDP_HOST, UDP_PORT))
        try:
            loguru_logger.log("RAW", self.create_send_msg(byte_msg))
        except Exception as e:
            None #ignore if script doesnt use logurj

        #self.ser.write(byte_msg)

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
        # ser.read can return an empty string
        # or raise a SerialException
        rx_bytes = self.sock.recv(13)

        header = (rx_bytes[0] & 0xF8)
        print("header = ", header)
        if (header) == 0xa8:
            #get the cob id
            cob_id = (rx_bytes[0] & 0x7) << 8 #move the 3bits up to the top
            cob_id |= (rx_bytes[1] & 0xFF)#append the bottom 8 bits
            remote_frame = (rx_bytes[2] & 0x80) >> 7
            extended_id = (rx_bytes[2] & 0x40) >> 6
            data_length = (rx_bytes[2] & 0xF)
            data = rx_bytes[3:11]
            #validate the crc
            # return None, False
            sock_data = bytearray()
            sock_data.append(0xB)
            sock_data.extend(rx_bytes)
            # received message data okay
            print("got here before message")
            msg = Message(
                timestamp=time.time(),
                arbitration_id=cob_id,
                is_remote_frame=remote_frame,
                is_extended_id=extended_id,
                data=data,
            )
            print("got here hooyah!")
            return msg, False
        else:
            print("exploded - returning none")
            return None, False

    def create_send_msg(self, tx_bytes):
        header = (tx_bytes[0] & 0xF8)
        msg = ""
        if (header) == 0xa8:
            # get the cob id
            cob_id = (tx_bytes[0] & 0x7) << 8  # move the 3bits up to the top
            cob_id |= (tx_bytes[1] & 0xFF)  # append the bottom 8 bits
            remote_frame = (tx_bytes[2] & 0x80) >> 7
            extended_id = (tx_bytes[2] & 0x40) >> 6
            data_length = (tx_bytes[2] & 0xF)
            data = tx_bytes[3:11]
            msg = f" id:{hex(cob_id)}: dl:{data_length}: d:{data.hex()}"
        return msg

    def create_recv_msg(self, rx_bytes):
        header = (rx_bytes[0] & 0xF8)
        msg = ""
        if (header) == 0xa8:
            # get the cob id
            cob_id = (rx_bytes[0] & 0x7) << 8  # move the 3bits up to the top
            cob_id |= (rx_bytes[1] & 0xFF)  # append the bottom 8 bits
            data_length = (rx_bytes[2] & 0xF)
            data = rx_bytes[3:11]
            index = struct.unpack("<H", rx_bytes[4:6])[0]
            subindex = rx_bytes[6]
            # if index == 0x5001 and subindex == 0x3:
            #     self.sock.sendto(data, (self.raw_udp_ip, 4001))
            msg = f" id:{hex(cob_id)}: dl:{data_length}: d:{data.hex()}"
        return msg


    @staticmethod
    def _detect_available_configs():
        channels = []
        serial_ports = []

        if list_ports:
            serial_ports = list_ports.comports()

        for port in serial_ports:
            channels.append({"interface": "serial", "channel": port.device})
        return channels

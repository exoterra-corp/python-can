import threading, queue, crcengine, binascii

class Receiver():
    """
    Simple Python receiver

    Puts frontend receive into thread and enqueues with thread-safe queue
    to minimize our chances of dropping messages. Currently made to be
    used with exoserial/pyserial front end.
    """
    def __init__(self, frontend):
        """
        Initalize the queue and setup access to the serial interface (frontend).
        """
        self.q = queue.Queue(5)
        self.running = True
        self.frontend = frontend
        self.t = threading.Thread(target=self.receive, daemon=True)  
        self.t.start()

    def receive(self):
        """
        receive, setups the serial port and if its open, reads 13 bytes and if its a good frame move onto the next byte.

        """
        frame = bytearray()
        msg = bytearray()
        self.frontend.reset_input_buffer()
        self.frontend.reset_output_buffer()
        while self.running:
            if self.frontend.isOpen():
                next_read = 13 - len(frame)
                msg = self.frontend.read(next_read)
                #print("msg len:", len(msg))
                if len(msg) > 0:
                    frame = frame + msg
                    if len(frame) == 13:
                        frame = self.good_frame(frame)

    def good_frame(self, frame):
        """
        good_frame, checks to make sure the crc is correct and if so put the frame into the return queue.
        """
        SOF = 0xa8
        byte_array = bytearray()
        valid_frame = False
        if frame[0] & 0xf8 == SOF:
            crcobj = crcengine.new("crc16-ibm")
            calc_crc = crcobj.calculate(frame[0:11]).to_bytes(2, byteorder="little")
            calc_crc = calc_crc[0] << 8 | calc_crc[1]
            frame_crc = frame[11] << 8 | frame[12]
            if calc_crc == frame_crc:
                self.q.put(frame)
                valid_frame = True
        if valid_frame == False:
            byte_array = bytearray(frame)
            print("invalid frame: ", binascii.hexlify(byte_array))
            byte_array.pop(0)
        return byte_array

    def thread_stop(self):
        """
        thread_stop, stops the loop.
        """
        self.running = False



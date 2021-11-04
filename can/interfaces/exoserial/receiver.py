import threading, queue, crcengine, binascii

'''
Simple Python receiver 

Puts frontend receive into thread and enqueues with thread-safe queue
to minimize our chances of dropping messages. Currently made to be 
used with exoserial/pyserial front end 
'''
class Receiver():

    def __init__(self, frontend):
        self.q = queue.Queue(5)
        self.running = True
        self.frontend = frontend
        self.t = threading.Thread(target=self.receive, daemon=True)  
        self.t.start()

    def good_frame(self, frame):
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

    def receive(self):
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

                #sof_byte = self.frontend.read(1)
                #if len(sof_byte) != 0:
                #    if sof_byte[0] & 0xf8 == SOF:
                #        # if start of frame byte found, read rest of payload
                #        payload = self.frontend.read(12)
                #        # put frame together
                #        frame = sof_byte + payload
                #        # calculate crc to make sure we didn't read a data byte instead of a
                #        #  start of frame byte
                #        crcobj = crcengine.new("crc16-ibm")
                #        calc_crc = crcobj.calculate(frame[0:11]).to_bytes(2, byteorder="little")
                #        calc_crc = calc_crc[0] <<8 | calc_crc[1]
                #        frame_crc = frame[11] << 8 | frame[12]
                #        ret = self.good_frame(frame)
                #        print("frame len:", ret)
                        # compare crcs
                        #if calc_crc == frame_crc:
                        #    # If crcs match, we can assume we have a valid message, queue it
                        #    self.q.put(frame)

    def thread_stop(self):
        self.running = False



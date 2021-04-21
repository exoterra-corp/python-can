import threading, queue, crcengine

'''
Simple Python receiver 

Puts frontend receive into thread and enqueues with thread-safe queue
to minimize our chances of dropping messages. Currently made to be 
used with exoserial/pyserial front end 
'''
class Receiver():
    qLen=5
    msg_length=13
    q = queue.Queue(qLen)
    def __init__(self, frontend):
        self.frontend = frontend
        self.t = threading.Thread(target=self.receive, daemon=True)  
        self.t.start()
        
    def receive(self):
        SOF = 0xa8
        packet = bytearray()
        while True:
            sof_byte = self.frontend.read(1)
            if len(sof_byte) != 0:
                if sof_byte[0] & 0xf8 == SOF:
                    # if start of frame byte found, read rest of payload
                    payload = self.frontend.read(12)
                    # put frame together
                    frame = sof_byte + payload
                    # calculate crc to make sure we didn't read a data byte instead of a
                    #  start of frame byte
                    crcobj = crcengine.new("crc16-ibm")
                    calc_crc = crcobj.calculate(frame[0:11]).to_bytes(2, byteorder="little")
                    calc_crc = calc_crc[0] <<8 | calc_crc[1]
                    frame_crc = frame[11] << 8 | frame[12] 
                    # compare crcs
                    if calc_crc == frame_crc:   
                        # If crcs match, we can assume we have a valid message, queue it
                        self.q.put(frame)


                 


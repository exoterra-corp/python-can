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
        self.stop_thread = False
        self.frontend = frontend
        self.t = threading.Thread(target=self.receive, daemon=True)  
        self.t.start()
       
    def receive(self):
        SOF = 0xa8
        packet = bytearray()
        while self.stop_thread == False:
            if self.frontend.is_open:
                frame = self.frontend.read(13)
                if len(frame) != 0:
                    valid_packet_found = False
                    while valid_packet_found != True:
                        if frame[0] & 0xf8 == SOF:
                            # calculate crc to make sure we didn't read a data byte instead of a
                            #  start of frame byte
                            crcobj = crcengine.new("crc16-ibm")
                            calc_crc = crcobj.calculate(frame[0:11]).to_bytes(2, byteorder="little")
                            calc_crc = calc_crc[0] << 8 | calc_crc[1]
                            frame_crc = frame[11] << 8 | frame[12] 
                            # compare crcs
                            if calc_crc == frame_crc:   
                                # If crcs match, we can assume we have a valid message, queue it
                                self.q.put(frame)                
                                valid_packet_found = True
                            else:
                                frame = frame[1:] 
                                if self.frontend.is_open:
                                    frame + self.frontend.read(1)
                                    valid_packet_found = False 

        print("Stopping thread rcvr thread")

    def thread_stop(self):
        self.stop_thread = True



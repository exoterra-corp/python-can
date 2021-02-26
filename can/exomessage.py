from . import Message

class ExoMessage(Message):
    def __init__(self,
                 node_cob_id,
                 data,
                 remote_transmission_request=0,
                 identifier_extension_bit=0,
                ):

        self.start_of_frame = (0xa8) #b10101
        self.node_cob_id:int = node_cob_id #default should be cob-id
        self.remote_transmission_request = remote_transmission_request #1bit
        self.identifier_extension_bit = identifier_extension_bit #1bit
        self.reserved_bits = 0 #2bits
        self.data_length = 8 #4bits
        self.data:float = data #8bytes of data
        self.crc:int = 0 #2bytes
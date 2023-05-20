import pickle
import time

CONNECTION = "CONNECTION"
AUTHENTICATION_CODE = "AUTHENTICATION CODE"
DISCONNECTION = "DISCONNECTION"

VERSION = "VERSION"
NAME = "NAME"

class Packet:

    def __init__(self, type_, packet_data, sender = None, time_sent = None, receiver = None, time_received = None):
        self.type = type_
        self.pakcet_data = packet_data
        self.sender = sender
        self.time_sent = time_sent
        self.receiver = receiver
        self.time_received = time_received

    def send(self, sender, time_sent):
        self.time_sent = time_sent
        self.sender = sender

        to_send = {
            "TYPE": self.type,
            "PACKET_DATA": self.pakcet_data,
            "SENDER": self.sender,
            "TIME_SENT": self.time_sent,
            "RECEIVER": self.receiver,
            "TIME_RECEIVED": self.time_received
        }

        return pickle.dumps(to_send)
    
    @classmethod
    def receive(cls, packet, receiver, time_recived):
        to_create = pickle.loads(packet)
        to_create["TIME_RECEIVED"] = time_recived
        to_create["RECEIVER"] = receiver
        
        new_pakcet = Packet(to_create["TYPE"], to_create["PACKET_DATA"], to_create["SENDER"], to_create["TIME_SENT"], to_create["RECEIVER"], to_create["TIME_RECEIVED"])
        return new_pakcet
    
    def copy(self):
        return Packet(self.type, self.pakcet_data)
    
    def __hash__(self):
        type_hash = hash(self.type)
        packet_data_hash = hash(self.pakcet_data)
        bit_hash = 128
        return type_hash * packet_data_hash * bit_hash
    
    def delay(self):
        if isinstance(self.time_sent, float) and isinstance(self.time_received, float):
            delay = self.time_received - self.time_sent
            return delay
        
        return None
    
if __name__ == "__main__":
    p = Packet("TEST", {"image": 11100101110000101010010100101000001111110101011100010100111010100101})
    data = p.send("Harry", time.time())
    time.sleep(1)
    newP = Packet.receive(data, "Pi", time.time())
    print(newP.delay())
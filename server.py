import socket
import packet
import random

class ConnectedClient:

    def __init__(self, connection, address) -> None:
        self.connection = connection
        self.address = address
        self.type = None
        self.authentication_code = None

class Server:

    def __init__(self) -> None:
        self.connect_clients = {}
        self.received_packets = []
        self.max_clients = 10

        self.port = 8000
        self.host = socket.gethostname()
        self.ip = socket.gethostbyname(self.host)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def generate_authentication_code(self, address):
        address_hash = hash(address)
        random_bit = random.random()
        random_int = random.randint(0, 1024)
        authentication_code = address_hash * random_bit * random_int
        return authentication_code

    def client_connection(self, connection, address):
        authentication_code = self.generate_authentication_code(connection, address)
        connection_packet = packet.Packet(packet.CONNECTION, {})
        while True:
            pass
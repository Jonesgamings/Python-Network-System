import socket
import packet
import random
import time
import _thread
import tkinter as tk

class ConnectedClient:

    def __init__(self, connection, address) -> None:
        self.connection = connection
        self.address = address
        self.type = None
        self.authentication_code = None
        self.version = ""

    def set_authentication_code(self, authentication_code):
        self.authentication_code = authentication_code

    def set_type(self, type_):
        self.type = type_

    def set_version(self, version):
        self.version = version

    def kick_client(self):
        disconnect_packet = packet.Packet(packet.DISCONNECTION, {packet.AUTHENTICATION_CODE: self.authentication_code})
        self.connection.send(disconnect_packet.send(self.socket, time.time()))
        self.connection.close()
        
class Server:

    def __init__(self) -> None:
        self.connected_clients = []
        self.max_clients = 10
        self.max_byte_length = 2048
        self.version = "1.0"
        self.running = False

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
        connection_packet = packet.Packet(packet.CONNECTION, {packet.AUTHENTICATION_CODE: authentication_code})
        connection.send(connection_packet.send(self.socket, time.time()))
        connection_client = ConnectedClient(connection, address)
        received_connection_pakcet = False

        while True:
            
            try:
                received_pakcet_bytes = connection.recv(self.max_byte_length)
                if received_pakcet_bytes:
                    received_pakcet = packet.Packet.receive(received_pakcet_bytes, self.socket, time.time())

                    #CONNECTION PACKET
                    if received_pakcet.type == packet.CONNECTION and not received_connection_pakcet:
                        data = received_pakcet.pakcet_data
                        if data[packet.AUTHENTICATION_CODE] == authentication_code:
                            connection_client.set_authentication_code(authentication_code)
                            connection_client.set_version(data[packet.VERSION])
                            self.connected_clients.append(connection_client)
                            received_connection_pakcet = True

                    #DISCONNECTION PACKET
                    elif received_pakcet.type == packet.DISCONNECTION:
                        if data[packet.AUTHENTICATION_CODE] == authentication_code:
                            connection.close()
                            self.connected_clients.remove(connection_client)

            except:
                pass

    def send_packet_all(self, packet):
        for client in self.connected_clients:
            packet_bytes = packet.send(self.socket, time.time())
            client.connection.send(packet_bytes)

    def kick_client(self, connection_client: ConnectedClient):
        connection_client.kick_client()
        self.connected_clients.remove(connection_client)

    def kick_all(self):
        for client in self.connected_clients.copy():
            client.kick_client()

        self.connected_clients.clear()

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.max_clients)
        self.connected_clients.clear()
        self.running = True

        while self.running:

            try:
                connection, address = self.socket.accept()
                _thread.start_new_thread(self.client_connection, (connection, address))

            except:
                pass

    def close(self):
        self.kick_all()
        self.running = False
        self.socket.close()

class ServerUI(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.server = Server()

        self.geometry("500x500")
        self.resizable(width = False , height = False)

        self.connected_clients_frame = tk.Frame(self, borderwidth=1, relief = tk.SOLID, width = 200, height = 200)
        self.start_button = tk.Button(self, text = "Start")
        self.stop_button = tk.Button(self, text = "Stop")

        self.connected_clients_frame.place(x = 100, y = 100)

    def start_server(self):
        pass

    def stop_server(self):
        pass

if __name__ == "__main__":
    ui = ServerUI()
    ui.mainloop()